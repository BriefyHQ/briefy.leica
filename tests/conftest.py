from briefy.common.utils.transformers import to_serializable
from briefy.leica.db import Base
from briefy.leica.db import create_engine
from briefy.leica.db import Session as DBSession
from briefy.ws.auth import AuthenticatedUser
from briefy.ws.config import JWT_EXPIRATION
from briefy.ws.config import JWT_SECRET
from datetime import datetime
from pyramid import testing
from pyramid_jwt.policy import JWTAuthenticationPolicy
from pyramid.paster import get_app
from webtest import TestApp

import configparser
import enum
import json
import pytest
import os
import uuid


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


@pytest.fixture(scope='class')
def sql_engine(request, db_settings):
    """Create new engine based on db_settings fixture.

    :param request: pytest request
    :param db_settings: database connection string from db_settings fixture.
    :return: sqlalcheny engine instance.
    """
    engine = create_engine(db_settings)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    def teardown():
        Base.metadata.drop_all(engine)

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
        DBSession.remove()

    request.addfinalizer(teardown)
    return connection


@pytest.fixture(scope='module')
def session():
    """Return session from database.

    :returns: A SQLAlchemy scoped session
    :rtype: sqlalchemy.orm.scoped_session
    """
    return DBSession()


@pytest.mark.usefixtures('db_transaction', 'create_dummy_request')
class BaseModelTest:
    """Base class to test all models."""
    cardinality = 1
    number_of_wf_transtions = 0
    dependencies = []
    file_path = ''
    payload_position = 0
    model = None
    request = None

    def setup_method(self, method):
        """Setup testing environment."""
        self.config = testing.setUp(request=self.request)
        app = get_app('configs/testing.ini#main')
        self.testapp = TestApp(app)

    def teardown_method(self, method):
        """Teardown testing environment."""
        testing.tearDown()

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

    def test_can_persist_model_instance(self):
        """Test if we can persist a model instance."""
        Model = self.model
        obj = Model.query().first()
        objs = Model.query().all()
        assert len(objs) == self.cardinality
        assert objs[0].id == obj.id
        assert objs[0].created_at == obj.created_at
        assert objs[0].updated_at == obj.updated_at

    def test_workflow(self, instance_obj):
        """Test if we have a workflow setup in here, some objects d'ont have."""
        wf = instance_obj.workflow
        if wf is not None:
            assert instance_obj.state == 'created'
            assert len(wf.transitions) == self.number_of_wf_transtions


@pytest.fixture(scope='class')
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
    obj = model.get(payload['id'])
    if not obj:
        obj = cls.model(**payload)
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
                obj = model(**payload)
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

        db_obj = self.model.query().get(payload['id'])

        # validate response payload against sent payload
        for key, value in payload.items():
            if key not in self.ignore_validation_fields:
                assert result.get(key) == value

        # state can be automatic changed by after_insert event listener
        assert self.initial_wf_state == result.get('state')

        # validate database model data against sent payload
        for key, value in payload.items():
            if key not in self.ignore_validation_fields:
                obj_value = getattr(db_obj, key)
                if isinstance(obj_value, (datetime, uuid.UUID, enum.Enum)):
                    obj_value = to_serializable(obj_value)
                assert obj_value == value

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
                if isinstance(value, (datetime, uuid.UUID, enum.Enum)):
                    value = to_serializable(value)
                assert result.get(key) == value

    def test_get(self, app, obj_payload):
        """Test get a collection of items."""
        request = app.get('{base}'.format(base=self.base_path),
                          headers=self.headers, status=200)
        result = request.json
        assert 'data' in result
        assert 'total' in result
        assert result['total'] == len(result['data'])

    def test_successful_update(self, obj_payload, app):
        """Teste put CustomerInfo to existing object."""
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

        updated_obj = self.model.get(obj_id)
        for key, value in payload.items():
            obj_value = getattr(updated_obj, key)
            if isinstance(obj_value, (datetime, uuid.UUID, enum.Enum)):
                obj_value = to_serializable(obj_value)
            assert obj_value == value

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
        assert error['description'] == 'The id informed is not 16 byte uuid valid.'

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
        assert error['description'] == 'The id informed is not 16 byte uuid valid.'


@pytest.fixture()
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
        "locale": "en_GB",
        "id": "669a99c2-9bb3-443f-8891-e600a15e3c10",
        "fullname": "Rudá Filgueiras",
        "first_name": "Rudá",
        "email": "rudazz@gmail.com",
        "last_name": "Filgueiras",
        "groups": ["g:briefy_qa", "g:briefy_pm"]
    }
    policy = JWTAuthenticationPolicy(private_key=JWT_SECRET,
                                     expiration=int(JWT_EXPIRATION))
    token = policy.create_token(user_payload['id'], **user_payload)
    cls = request.cls
    cls.token = token
    return user_payload


@pytest.fixture('class')
def create_dummy_request(request, login):
    """Create and attach a DummyRequest on the test class."""
    dummy_request = testing.DummyRequest()
    user_id = login.pop('id')
    dummy_request.user = AuthenticatedUser(user_id, login)
    # this request is py.test request (who declare the fixture)
    cls = request.cls
    # this request is web request
    cls.request = dummy_request
