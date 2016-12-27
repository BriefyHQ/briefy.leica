from briefy.leica import logger
from briefy.leica.sync.user import get_rosetta
from briefy.knack.base import KnackEntity
from sqlalchemy_utils import PhoneNumber

import briefy.knack as knack
import uuid


def get_model_and_data(model_name):
    """Load model and data dump from Knack"""
    logger.info('Retrieving {0} model from Knack'.format(model_name))
    model = knack.get_model(model_name)
    logger.info('Querying all existing {0}s'.format(model_name))
    all_items = model.query.all()
    logger.info('Fetched {0} {1}s from Knack'.format(len(all_items), model_name))
    return model, all_items


class Auto:
    """Helper class to map dict to object."""

    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def __getattr__(self, attr):
        return ''


class ModelSync:
    """Sync object from knack to sqlalchemy model."""

    model = None
    knack_model = None
    knack_model_name = ''
    created = {}
    updated = {}
    knack_parents = None
    knack_parent_model = ''
    parent_model = None
    bulk_insert = False
    bulk_insert_items = None
    batch_size = 10

    def __init__(self, session, transaction, parent=None):
        """Initialize syncronizer"""
        self.session = session
        self.transaction = transaction
        self.parent = parent
        self.created = {}
        self.updated = {}
        self.rosetta = get_rosetta()
        self.bulk_insert_items = []

    def get_knack_item(self, knack_id) -> object:
        """Get one item from knack service."""
        if not self.knack_model:
            self.knack_model = knack.get_model(self.knack_model_name)
        return self.knack_model.get(knack_id)

    def get_items(self):
        """Get all items for one knack model."""
        self.knack_model, items = get_model_and_data(self.knack_model_name)
        return items

    def get_payload(self, kobj, briefy_id=None):
        """Create payload from knack obj."""
        briefy_id = briefy_id or str(uuid.uuid4())
        return dict(id=briefy_id)

    def get_user(self, kobj, attr):
        """Map knack user ID to rolleiflex user ID."""
        kuser = getattr(kobj, attr, None)
        if kuser:
            return self.rosetta.get(kuser[0]['id'])
        else:
            return None

    def get_local_roles(self, kobj, attr) -> list:
        """Return a list of local users ID from the list of knack users."""
        knack_roles = getattr(kobj, attr, None)
        result = []
        for krole in knack_roles:
            briefy_user = self.rosetta.get(krole['id'])
            if briefy_user:
                result.append(briefy_user)
        return result

    def update_local_roles(self, obj, new_users, attr):
        """Update local roles for DB objects using a list of roles."""
        actual_users = [role.user_id for role in obj.local_roles if role.role_name == attr]
        for user_id in new_users:
            if user_id not in actual_users:
                obj._add_local_role_user_id(user_id, attr)

    def update(self, kobj, item):
        """Update database item from knack obj."""
        payload = self.get_payload(kobj, item.id)
        for key, value in payload.items():
            setattr(item, key, value)
        model_name = self.model.__name__
        logger.debug('{model_name} updated: {id}'.format(model_name=model_name,
                                                         id=item.id))

    def parse_decimal(self, value):
        """Parse decimal money values to integer."""
        return value * 100 if value else 0

    def parse_phonenumber(self, kobj, attr):
        """Parse phone number from knack before input in the database."""
        number_attr = getattr(kobj, attr, None)
        if number_attr:
            number = number_attr.get('number')
            number = number.strip('-')
            number = number.strip(' ')
            try:
                if number[:2] == '00':
                    print('Assuming international number: {0}.'.format(number))
                    number = '+' + number[2:]
                elif number[:1] == '0':
                    pass
                elif len(number) > 10 and number[0] != '+':
                    print('Assuming international number: {0}.'.format(number))
                    number = '+' + number

                number = PhoneNumber(number)
            except Exception as exc:
                msg = 'Briefy ID: {0} Number: {1}. Error: {2}'
                print(msg.format(kobj.briefy_id, number, exc))
                number = None
        else:
            number = None

        return number

    def get_parent(self, kobj: KnackEntity, field_name: str ='',
                   knack_parent_model=None, parent_model=None) -> tuple:
        """Get parent objects (knack and model instance) for one item."""
        if not knack_parent_model:
            knack_parent_model = self.knack_parent_model
        if not parent_model:
            parent_model = self.parent_model

        if not self.knack_parents:
            _, self.knack_parents = get_model_and_data(knack_parent_model)
        knack_parent = None
        for item in self.knack_parents:
            value_id = getattr(kobj, field_name)[0]['id']
            if item.id == value_id:
                knack_parent = item
                break

        db_parent = parent_model.query().filter_by(external_id=knack_parent.id).one()
        return db_parent, knack_parent

    def add(self, kobj, briefy_id):
        """Add new database item from knack obj."""
        session = self.session
        payload = self.get_payload(kobj, briefy_id)
        model_name = self.model.__name__
        if not self.bulk_insert:
            obj = self.model(**payload)
            session.add(obj)
            session.flush()
            logger.debug('{model_name} added: {id}'.format(model_name=model_name,
                                                           id=obj.id))
            return obj
        else:
            self.bulk_insert_items.append(payload)
            logger.debug('{model_name} included in the bulk insert: {id}'.format(
                model_name=model_name,
                id=payload.get('id')
            ))
            return payload

    def sync_knack(self):
        """Sync all created objects back to knack updating briefy_id."""
        objs_map = list(self.created.items()) + list(self.updated.items())
        logger.debug('Begin to sync back knack items.')
        for briefy_id, kobj in objs_map:
            if kobj.briefy_id:
                continue
            else:
                kobj.briefy_id = str(briefy_id)
                knack.commit_knack_object(kobj, only_fields=['briefy_id'])

    def get_db_item(self, kobj):
        """Try to find existent db item for a kobj."""
        item = None
        briefy_id = kobj.briefy_id
        if briefy_id:
            item = self.model.get(briefy_id)

        if hasattr(self.model, 'external_id') and not item:
            filter_query = self.model.query().filter_by(external_id=kobj.id)
            item = filter_query.one_or_none()

        return item

    def __call__(self, knack_id=None):
        """Syncronize one or all items from knack to sqlalchemy model."""
        created = self.created
        updated = self.updated
        model_name = str(self.model.__name__)
        items = []

        if knack_id:
            item = self.get_knack_item(knack_id)
            if item:
                items.append(item)
        else:
            items = self.get_items()

        # items = items[0:710]
        total = len(items)
        for i, kobj in enumerate(items):
            item = self.get_db_item(kobj)
            if item:
                logger.debug('Try to update item {0}: {1} of {2}'.format(model_name, i, total))
                self.update(kobj, item)
                updated[item.id] = kobj
            else:
                logger.debug('Try to add item {0}: {1} of {2}'.format(model_name, i, total))
                item = self.add(kobj, kobj.briefy_id)
                if not self.bulk_insert:
                    created[item.id] = kobj
            if i % self.batch_size == 0:
                self.transaction.commit()

            if i % 100 == 0:
                logger.info('Updated / Added {items} {model}s'.format(items=i, model=model_name))

        if self.bulk_insert:
            self.session.bulk_insert_mappings(self.model, self.bulk_insert_items)

        self.transaction.commit()
        self.sync_knack()
        msg = '{model} created: {created} / {model} updated: {updated}'.format(
            model=model_name,
            created=len(created),
            updated=len(updated)
        )
        logger.info(msg)
        return created, updated
