"""Conftest for Leica."""
from briefy import leica
from briefy.common.db import datetime_utcnow
from briefy.common.types import BaseUser
from briefy.common.utils.transformers import to_serializable
from briefy.leica import models
from briefy.leica.db import Session as DBSession
from briefy.leica.db import Base
from briefy.leica.db import create_engine
from briefy.ws.config import JWT_EXPIRATION
from briefy.ws.config import JWT_SECRET
from datetime import date
from datetime import datetime
from octopus.lens import EasyUUID
from prettyconf import config
from pyramid.paster import get_app
from pyramid.testing import DummyRequest
from pyramid_jwt.policy import JWTAuthenticationPolicy
from sqlalchemy_utils import PhoneNumber
from webtest import TestApp
from zope.configuration.xmlconfig import XMLConfig

import botocore
import briefy.common
import configparser
import enum
import json
import os
import pytest
import requests
import uuid


XMLConfig('configure.zcml', briefy.common)()
XMLConfig('configure.zcml', leica)()


@pytest.fixture(scope='session', autouse=True)
def mock_boto():
    """Mock botocore endpoint to use the docker image."""
    host = config('SQS_IP', default='127.0.0.1')
    port = config('SQS_PORT', default='5000')
    queue_url = 'http://{host}:{port}'.format(host=host, port=port)

    class MockEndpoint(botocore.endpoint.Endpoint):
        def __init__(self, host, *args, **kwargs):
            super().__init__(queue_url, *args, **kwargs)

    if not hasattr(botocore.endpoint, 'OrigEndpoint'):
        botocore.endpoint.OrigEndpoint = botocore.endpoint.Endpoint
    botocore.endpoint.Endpoint = MockEndpoint


@pytest.fixture(scope='session')
def db_settings():
    """Get database configuration from .ini file.

    :return: database connection string from pyramid config.
    :rtype: str
    """
    CONFIG_PATH = (__file__.rsplit('/', 2)[0] + '/configs')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH + '/testing.ini')
    return config.get('app:main', 'sqlalchemy.url')


@pytest.fixture(scope='session')
def sql_engine(request, db_settings):
    """Create new engine based on db_settings fixture.

    :param request: pytest request
    :param db_settings: database connection string from db_settings fixture.
    :return: sqlalcheny engine instance.
    """
    engine = create_engine(db_settings)
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def teardown():
        if 'transaction' in Base.metadata.tables:
            transaction_table = Base.metadata.tables['transaction']
            Base.metadata.remove(transaction_table)
        Base.metadata.drop_all(engine)
        if 'transaction' in Base.metadata.tables:
            DBSession.execute('DROP SEQUENCE transaction_id_seq CASCADE;')

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope='class')
def db_transaction(request, sql_engine):
    """Create a transaction for each test class.

    :param request: pytest request
    :param sql_engine: sqlalchemy engine (fixture)
    :return: sqlalchemy connection
    """
    connection = sql_engine.connect()
    transaction = connection.begin()
    DBSession.configure(bind=connection)

    def teardown():
        transaction.rollback()
        connection.close()

    request.addfinalizer(teardown)
    return connection


@pytest.fixture(scope='class')
def session(request):
    """Return session from database.

    :returns: A SQLAlchemy scoped session
    :rtype: sqlalchemy.orm.scoped_session
    """
    db_session = DBSession()

    def teardown():
        DBSession.remove()

    request.addfinalizer(teardown)
    return db_session


@pytest.fixture(scope='function')
def web_request():
    """Return a web request instance.

    :returns: DummyRequest
    :rtype: pyramid.testing.DummyRequest
    """
    req = DummyRequest()
    req.validated = {}
    return req


@pytest.fixture(scope='function')
def now_utc():
    """Fixture to return a datetime now instance with timezone.

    :returns: datetime.now with timezone
    :rtype: datetime.datetime
    """
    return datetime_utcnow()


@pytest.mark.usefixtures('db_transaction')
class BaseModelTest:
    """Base class to test all models."""

    cardinality = 1
    number_of_wf_transtions = 0
    dependencies = []
    file_path = ''
    payload_position = 0
    model = None
    request = None
    initial_wf_state = 'created'

    def test_obj_is_instance_of_model(self, instance_obj):
        """Test if the created object is an instance of self.model klass."""
        Model = self.model
        assert isinstance(instance_obj, Model)

    def test_get(self, instance_obj, obj_payload):
        """Test Obj.get method."""
        Model = self.model
        id = obj_payload.get('id')
        obj = Model.get(id)
        assert obj is not None
        assert instance_obj == obj

    def test_query(self):
        """Test Model.query method."""
        Model = self.model
        obj = Model.query().first()
        assert self.cardinality == Model.query().count()
        assert obj in Model.query().all()

    def test_can_persist_model_instance(self, obj_payload):
        """Test if we can persist a model instance."""
        Model = self.model
        obj = Model.query().first()
        objs = Model.query().all()
        assert len(objs) == self.cardinality

        # composed primary keys
        if isinstance(obj_payload['id'], list):
            new_payload = dict(obj_payload.items())
            new_payload.pop('id')
            for key, value in new_payload.items():
                assert getattr(objs[0], key) == getattr(obj, key)
        else:
            assert objs[0].id == obj.id

        assert objs[0].created_at == obj.created_at
        assert objs[0].updated_at == obj.updated_at

    def test_to_dict_respects_excludes(self, instance_obj):
        """Test to_dict will respect __exclude_attributes__ ."""
        not_expected_attributes = set(self.model.__exclude_attributes__)
        obj_dict = instance_obj.to_dict(excludes=[], includes=[])
        intersection = [k for k in obj_dict.keys() if k in not_expected_attributes]
        assert len(intersection) == 0

    def test_to_dict_additional_attr(self, instance_obj):
        """Test to_dict will respect __to_dict_additional_attributes__ ."""
        additional_attributes = set(self.model.__to_dict_additional_attributes__)
        obj_dict = instance_obj.to_dict(excludes=[], includes=[])
        keys = obj_dict.keys()
        missing = [k for k in additional_attributes if k not in keys]
        assert len(missing) == 0

    def test_to_dict_respects__summary_attributes_relations(self, instance_obj):
        """Test to_dict will respect __summary_attributes_relations__ ."""
        to_summary_relations = set(self.model.__summary_attributes_relations__)
        obj_dict = instance_obj.to_dict(excludes=[], includes=[])
        intersection = [k for k in obj_dict.keys() if k in to_summary_relations]
        assert len(intersection) == len(to_summary_relations)

    def test_to_summary_dict(self, instance_obj):
        """Test to_summary_dict for this model."""
        expected_attributes = set(self.model.__summary_attributes__)
        summary_dict = instance_obj.to_summary_dict()
        item_attributes = {k for k in summary_dict.keys()}
        assert item_attributes == expected_attributes

    def test_workflow(self, instance_obj):
        """Test if we have a workflow setup in here, some objects d'ont have."""
        wf = instance_obj.workflow
        if wf is not None:
            assert instance_obj.state == self.initial_wf_state
            assert len(wf.transitions) == self.number_of_wf_transtions


@pytest.mark.usefixtures('db_transaction')
class BaseLocationTest(BaseModelTest):
    """Base class to test locations."""

    def test_working_location_base_class(self, instance_obj):
        """Test inheritance to models.WorkingLocation."""
        assert isinstance(instance_obj, leica.models.WorkingLocation)


@pytest.mark.usefixtures('db_transaction')
class BaseLinkTest(BaseModelTest):
    """Base class to test Links."""

    social = True

    def test_link_base_class(self, instance_obj):
        """Test inheritance to models.Link."""
        assert isinstance(instance_obj, leica.models.Link)

    def test_is_social(self, instance_obj):
        """Test is_social flat."""
        assert instance_obj.is_social is self.social


@pytest.fixture(scope='function')
def instance_obj(request, session, obj_payload):
    """Create instance object an dependencies using hook methods.

    :param request: pytest request object
    :param session: sqlalchemy session
    :return:
    """
    cls = request.cls
    model = request.cls.model
    if hasattr(cls, 'create_dependencies'):
        cls.create_dependencies(session)

    payload = obj_payload

    obj_id = payload['id']
    obj_id = EasyUUID(obj_id) if not isinstance(obj_id, list) else obj_id
    obj = model.get(obj_id)
    if not obj:
        # composed primary keys
        if isinstance(obj_id, list):
            new_payload = dict(payload.items())
            new_payload.pop('id')
            obj = cls.model.create(new_payload)
        else:
            payload['id'] = obj_id
            obj = cls.model.create(payload)
        session.add(obj)
        session.flush()
    return obj


@pytest.fixture(scope='class')
def obj_payload(request):
    """Return from file the first registry to create instance data.

    :return: dict with payload for object instance.
    """
    cls = request.cls
    if getattr(cls, 'get_payload', None) is not None:
        return cls.get_payload()
    else:
        abs_path = os.path.join(__file__.rsplit('/', 1)[0], cls.file_path)
        with open(abs_path) as file:
            data = json.load(file)
        return data[cls.payload_position]


@pytest.fixture
def obj_payload_other(file_path, position):
    """Return from file the payload in the informed position.

    :return: dict with payload for object instance.
    """
    abs_path = os.path.join(__file__.rsplit('/', 1)[0], file_path)
    with open(abs_path) as file:
        data = json.load(file)
    return data[position]


@pytest.fixture(scope='class')
def create_dependencies(request, session):
    cls = request.cls
    for model, file_path in cls.dependencies:
        abs_path = os.path.join(__file__.rsplit('/', 1)[0], file_path)
        with open(abs_path) as file:
            data = json.load(file)
        for payload in data:
            obj = model.get(payload['id'])
            if not obj:
                obj = model.create(payload)
                session.add(obj)
    session.flush()


@pytest.mark.usefixtures('db_transaction', 'login')
class BaseTestView:
    """BaseTestView class"""

    auth_header = None
    base_path = ''
    dependencies = []
    file_path = ''
    model = None
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    payload_position = 0
    update_map = {}
    serialize_attrs = ['path', '_roles', '_actors']
    initial_wf_state = 'created'
    ignore_validation_fields = ['state_history', 'state']

    @property
    def headers(self):
        return {'X-Locale': 'en_GB',
                'Authorization': 'JWT {token}'.format(token=self.token)}

    def test_options(self, app):
        """Test OPTIONS verb."""
        req = app.options(
            self.base_path, status=200,
            headers={'Origin': 'lolnet.org',
                     'Access-Control-Request-Method': 'POST'})
        assert 'application/json' == req.content_type

    def test_options_with_no_headers(self, app):
        """Test OPTIONS verb without any header."""
        req = app.options(self.base_path, status=400)
        assert 'application/json' == req.content_type
        assert 'error' == req.json['status']
        assert 2 == len(req.json['errors'])

    def test_successful_creation(self, obj_payload, app):
        """Test successful creation of a new model."""
        payload = obj_payload
        request = app.post_json(self.base_path, payload, headers=self.headers, status=200)

        assert 'application/json' == request.content_type
        result = request.json

        db_obj = self.model.get(payload['id'])
        self.ignore_validation_fields.extend(self.model.__actors__)

        # validate response payload against sent payload
        for key, value in payload.items():
            if key not in self.ignore_validation_fields:
                result_value = result.get(key)
                if isinstance(value, list):
                    for item in result_value:
                        assert item in value
                else:
                    assert result_value == value

        # state can be automatic changed by after_insert event listener
        assert self.initial_wf_state == result.get('state')

        # validate database model data against sent payload
        for key, value in payload.items():
            if key not in self.ignore_validation_fields:
                obj_value = getattr(db_obj, key)
                if isinstance(obj_value, (date, datetime, uuid.UUID, enum.Enum, PhoneNumber)):
                    obj_value = to_serializable(obj_value)

                if isinstance(value, list):
                    for item in obj_value:
                        assert item in value
                else:
                    assert obj_value == value

        # state can be automatic changed by after_insert event listener
        assert self.initial_wf_state == getattr(db_obj, 'state')

    def test_get_item(self, app, obj_payload):
        """Test get a item."""
        payload = obj_payload
        obj_id = payload['id']
        request = app.get('{base}/{id}'.format(base=self.base_path, id=obj_id),
                          headers=self.headers, status=200)
        result = request.json
        db_obj = self.model.query().get(obj_id)

        for key, value in db_obj.to_dict().items():
            if key not in self.ignore_validation_fields:
                if isinstance(value, (date, datetime, uuid.UUID, enum.Enum, PhoneNumber)):
                    value = to_serializable(value)
                elif key in self.serialize_attrs:
                    value = json.loads(json.dumps(value, default=to_serializable))

                result_value = result.get(key)

                if isinstance(value, list):
                    for item in result_value:
                        assert item in value
                else:
                    assert result_value == value

        # state can be automatic changed by after_insert event listener
        assert self.initial_wf_state == getattr(db_obj, 'state')

    def test_get_collection(self, app):
        """Test get a collection of items."""
        request = app.get('{base}'.format(base=self.base_path),
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data'])

    def test_get_collection_item_attributes(self, app):
        """Test item attributes on a collection."""
        request = app.get(f'{self.base_path}', headers=self.headers, status=200)
        result = request.json
        item = result['data'][0]
        expected_attributes = set(self.model.__listing_attributes__)
        item_attributes = {k for k in item.keys()}
        assert item_attributes == expected_attributes

    def test_successful_update(self, obj_payload, app):
        """Teste put Data to existing object."""
        payload = self.update_map
        obj_id = obj_payload['id']
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=200)
        result = request.json
        assert 'application/json' == request.content_type

        # validate response payload against sent payload
        for key, value in payload.items():
            if key not in self.ignore_validation_fields:
                assert result.get(key) == value

        # state can be automatic changed by after_insert event listener
        assert self.initial_wf_state == result.get('state')

        updated_obj = self.model.get(obj_id)
        for key, value in payload.items():
            obj_value = getattr(updated_obj, key)
            if isinstance(obj_value, (date, datetime, uuid.UUID, enum.Enum)):
                obj_value = to_serializable(obj_value)
                assert obj_value == value
            elif isinstance(obj_value, list):
                for item in obj_value:
                    assert item in value
            else:
                assert obj_value == value

        # state can be automatic changed by after_insert event listener
        assert self.initial_wf_state == getattr(updated_obj, 'state')

    def test_get_not_found(self, app):
        """Test return 404 for valid UUID but do not refer to any obj."""
        obj_id = uuid.uuid4()
        request = app.get('{base}/{id}'.format(base=self.base_path, id=obj_id),
                          headers=self.headers, status=404)
        result = request.json

        assert result['status'] == 'error'
        assert self.NOT_FOUND_MESSAGE.format(obj_id) in result['message']

    def test_get_invalid_id(self, app):
        """Confirm failure when try to use invalid UUID as id."""
        obj_id = 'blabla'
        request = app.get('{base}/{id}'.format(base=self.base_path, id=obj_id),
                          headers=self.headers, status=400)
        result = request.json
        error = result['errors'][0]

        assert result['status'] == 'error'
        assert error['name'] == 'id'
        assert error['location'] == 'path'
        assert 'uuid' in error['description'].lower()

    def test_put_invalid_id(self, app, obj_payload):
        """Confirm failure when try to use invalid UUID as id."""
        payload = obj_payload
        obj_id = 'blabla'
        request = app.put_json('{base}/{id}'.format(base=self.base_path, id=obj_id),
                               payload, headers=self.headers, status=400)
        result = request.json
        error = result['errors'][0]

        assert result['status'] == 'error'
        assert error['name'] == 'id'
        assert error['location'] == 'path'
        assert 'uuid' in error['description'].lower()


@pytest.mark.usefixtures('db_transaction', 'login')
class BaseVersionedTestView(BaseTestView):
    """Test resources with versions."""

    check_versions_field = '_title'

    def test_versions_get_item(self, app, obj_payload):
        """Test get a item."""
        payload = obj_payload
        obj_id = payload['id']
        # Get original version
        request = app.get(
            '{base}/{id}/versions/0'.format(
                base=self.base_path, id=obj_id
            ),
            headers=self.headers,
            status=200
        )
        result = request.json
        db_obj = self.model.query().get(obj_id)
        obj_field = self.check_versions_field
        result_field = obj_field[1:] if obj_field.startswith('_') else obj_field
        version = db_obj.versions[0]
        assert to_serializable(getattr(version, obj_field)) == result[result_field]
        version = db_obj.versions[1]
        assert to_serializable(getattr(version, obj_field)) != result[result_field]

    def test_versions_get_item_wrong_id(self, app, obj_payload):
        """Test get a item passing the wrong id."""
        payload = obj_payload
        obj_id = payload['id']
        # Get version 42 (does not exist here)
        request = app.get(
            '{base}/{id}/versions/42'.format(
                base=self.base_path, id=obj_id
            ),
            headers=self.headers,
            status=404
        )
        result = request.json
        assert 'with version: 42 not found' in result['message']

    def test_versions_get_collection(self, app, obj_payload):
        """Test get list of versions of an item."""
        payload = obj_payload
        obj_id = payload['id']
        request = app.get(
            '{base}/{id}/versions'.format(
                base=self.base_path, id=obj_id
            ),
            headers=self.headers,
            status=200
        )
        result = request.json
        assert 'versions' in result
        assert 'total' in result
        assert result['total'] == len(result['versions'])

        assert 'id' in result['versions'][0]
        assert 'updated_at' in result['versions'][0]
        assert 'id' in result['versions'][1]
        assert 'updated_at' in result['versions'][1]

        assert result['versions'][1]['id'] > result['versions'][0]['id']
        assert result['versions'][1]['updated_at'] > result['versions'][0]['updated_at']


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class BaseDashboardTestView:
    """Test dashboards view base class."""

    # tuple of dashboards endpoints
    base_paths = ()

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Assignment, 'data/assignments.json')
    ]

    @property
    def headers(self):
        return {'X-Locale': 'en_GB',
                'Authorization': 'JWT {token}'.format(token=self.token)}

    def test_get_dashboards(self, app):
        """Test get all dashboards defined in the base_paths tuple."""
        headers = self.headers
        for path in self.base_paths:
            request = app.get(
                path,
                headers=headers,
                status=200
            )

            result = request.json
            assert 'data' in result
            assert 'columns' in result
            assert 'columns' in result
        # TODO: implement more checks about dashboard structure


@pytest.mark.usefixtures('db_transaction', 'create_dependencies')
class BaseTaskTest:
    """Test tasks."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Pool, 'data/jpools.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Assignment, 'data/assignments.json')
    ]

    def _setup_queue(self):
        """Return a queue instance."""
        from briefy.common.queue.event import EventQueue
        from briefy.common.queue import IQueue
        from zope.component import provideUtility

        import boto3

        name = 'foo'
        sqs = boto3.resource('sqs', region_name='us-east-1')
        sqs.create_queue(QueueName=name)
        self.queue = sqs.get_queue_by_name(QueueName=name)

        for message in self.queue.receive_messages(MaxNumberOfMessages=100):
            message.delete()

        EventQueue._queue = self.queue
        provideUtility(EventQueue, IQueue, 'events.queue')

    def setup_method(self, method):
        """Setup method."""
        self._setup_queue()

    def get_messages_from_queue(self):
        messages = self.queue.receive_messages(MaxNumberOfMessages=100)
        return messages


@pytest.fixture(scope='session')
def app():
    """Fixture to create new app instance.

    :return: pyramid wsgi app.
    """
    _app = get_app('configs/testing.ini#main')
    return TestApp(_app)


@pytest.fixture('class')
def login(request):
    """Login and get JWT token."""
    user_payload = {
        'locale': 'en_GB',
        'id': '669a99c2-9bb3-443f-8891-e600a15e3c10',
        'fullname': 'Rudá Filgueiras',
        'first_name': 'Rudá',
        'email': 'rudazz@gmail.com',
        'last_name': 'Filgueiras',
        'groups': [
            'g:briefy_qa',
            'g:briefy_pm',
            'g:briefy_bizdev',
            'g:briefy_scout',
            'g:briefy_finance',
            'g:briefy_support',
            'g:briefy'
        ]
    }
    policy = JWTAuthenticationPolicy(private_key=JWT_SECRET,
                                     expiration=int(JWT_EXPIRATION))
    token = policy.create_token(user_payload['id'], **user_payload)
    cls = request.cls
    cls.token = token
    return user_payload


@pytest.fixture
def login_as_customer():
    """Login and get JWT token."""
    user_payload = {
        'locale': 'en_GB',
        'id': '83c0ea60-1d60-4d4b-2c63-0e5bfad1ef9d',
        'fullname': 'Maike Bork',
        'first_name': 'Maike',
        'email': 'maike@lieferheld.de',
        'last_name': 'Borke',
        'groups': [
            'g:customers'
        ]
    }
    policy = JWTAuthenticationPolicy(private_key=JWT_SECRET,
                                     expiration=int(JWT_EXPIRATION))
    token = policy.create_token(user_payload['id'], **user_payload)
    return (user_payload, token)


@pytest.fixture
def login_as_professional():
    """Login and get JWT token."""
    user_payload = {
        'locale': 'en_GB',
        'id': '23d94a43-3947-42fc-958c-09245ecca5f2',
        'fullname': 'Sebastiao Salgado',
        'first_name': 'Sebastiao',
        'email': 'salgado@professional.briefy.co',
        'last_name': 'Salgado',
        'groups': [
            'g:professionals'
        ]
    }
    policy = JWTAuthenticationPolicy(private_key=JWT_SECRET,
                                     expiration=int(JWT_EXPIRATION))
    token = policy.create_token(user_payload['id'], **user_payload)
    return (user_payload, token)


def _mock_rolleiflex(self, method, url, *args, **kwargs):
    status_code = 200
    payload = kwargs.get('data', '')
    if 'internal/login' in url:
        filename = 'data/rolleiflex_login.json'
        # Wrong username
        if 'foo@bar.com' in payload:
            status_code = 404
    elif '/transitions' in url:
        filename = 'data/rolleiflex_user_transition.json'
    elif 'internal/user' in url:
        filename = 'data/user.json'
        # Not existing user:
        if '645fd371-b88d-4700-96a3-4692bb932ccb' in url:
            status_code = 404
    elif 'users' in url:
        filename = 'data/user.json'
        if '7645fd371-b88d-4700-96a3-4692bb932ccb' in payload:
            status_code = 405
        elif '8645fd371-b88d-4700-96a3-4692bb932ccb' in payload:
            status_code = 405
            filename = 'data/rolleiflex_failed_user_creation.json'
        elif '9645fd371-b88d-4700-96a3-4692bb932ccb' in payload:
            status_code = 405
            filename = 'data/rolleiflex_failed_user_creation.txt'
    headers = {
        'content-type': 'application/json',
    }
    data = open(os.path.join(__file__.rsplit('/', 1)[0], filename)).read()
    resp = requests.Response()
    resp.status_code = status_code
    resp.headers = headers
    resp._content = data.encode('utf8')
    return resp


def _mock_geonames(self, method, url, *args, **kwargs):
    status_code = 200
    headers = {'content-type': 'application/json'}
    filename = 'data/timezone.json'
    if 'lat=91' in url:
        filename = 'data/timezone_no_user.json'
    elif 'lng=181' in url:
        filename = 'data/timezone_ratelimit.json'
    data = open(os.path.join(__file__.rsplit('/', 1)[0], filename)).read()
    if 'lat=92'in url:
        # An invalid JSON response
        data = '{-'
    resp = requests.Response()
    resp.status_code = status_code
    resp.headers = headers
    resp._content = data.encode('utf8')
    return resp


@pytest.fixture(scope='session')
def mock_request():
    def mock_requests_response(self, method, url, *args, **kwargs):
        """Mock a response"""
        if 'briefy-thumbor' in url:
            filename = 'data/thumbor.json'
        elif 'api.geonames.org' in url:
            return _mock_geonames(self, method, url, *args, **kwargs)
        elif 'briefy-rolleiflex' in url:
            return _mock_rolleiflex(self, method, url, *args, **kwargs)
        status_code = 200
        headers = {
            'content-type': 'application/json',
        }
        data = open(os.path.join(__file__.rsplit('/', 1)[0], filename)).read()
        resp = requests.Response()
        resp.status_code = status_code
        resp.headers = headers
        resp._content = data.encode('utf8')
        return resp
    return mock_requests_response


@pytest.fixture(autouse=True)
def mock_api(monkeypatch, mock_request):
    """Mock all api calls."""
    monkeypatch.setattr(requests.sessions.Session, 'request', mock_request)


@pytest.fixture('session')
def roles():
    """Mock request to briefy-thumbor."""
    data = json.load(open(os.path.join(__file__.rsplit('/', 1)[0], 'data/roles.json')))
    roles = {
        k: BaseUser(data[k]['id'], data=data[k])
        for k in data
    }
    return roles
