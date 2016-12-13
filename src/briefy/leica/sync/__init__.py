from briefy.leica import logger
from briefy.leica.sync.user import get_rosetta

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

    def __init__(self, session, parent=None):
        """Initialize syncronizer"""
        self.session = session
        self.parent = parent
        self.created = {}
        self.updated = {}
        self.rosetta = get_rosetta()

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

    def get_user(self, kobj, attr=''):
        kuser = getattr(kobj, attr, None)
        if kuser:
            return self.rosetta.get(kuser[0]['id'])
        else:
            return None

    def update(self, kobj, item):
        """Update database item from knack obj."""
        payload = self.get_payload(kobj, item.id)
        for key, value in payload.items():
            setattr(item, key, value)
        model_name = self.model.__name__
        logger.debug('{model_name} updated: {id}'.format(model_name=model_name,
                                                         id=item.id))

    def add(self, kobj, briefy_id):
        """Add new database item from knack obj."""
        session = self.session
        payload = self.get_payload(kobj, briefy_id)
        obj = self.model(**payload)
        session.add(obj)
        session.flush()
        model_name = self.model.__name__
        logger.debug('{model_name} added: {id}'.format(model_name=model_name,
                                                       id=obj.id))
        return obj

    def sync_knack(self):
        """Sync all created objects back to knack updating briefy_id."""
        objs_map = list(self.created.items()) + list(self.updated.items())
        logger.debug('Begin to sync back knack items.')
        for briefy_id, kobj in objs_map:
            if kobj.briefy_id:
                continue
            else:
                kobj.briefy_id = briefy_id
                knack.commit_knack_object(kobj, only_fields=['briefy_id'])

    def get_db_item(self, kobj):
        """Try to find existent db item for a kobj."""
        item = None
        if hasattr(self.model, 'external_id'):
            filter_query = self.model.query().filter_by(external_id=kobj.id)
            item = filter_query.one_or_none()

        if not item:
            briefy_id = kobj.briefy_id
            if briefy_id:
                item = self.model.get(briefy_id)

        return item

    def __call__(self, knack_id=None):
        """Syncronize one or all items from knack to sqlalchemy model."""
        created = self.created
        updated = self.updated
        items = []

        if knack_id:
            item = self.get_knack_item(knack_id)
            if item:
                items.append(item)
        else:
            items = self.get_items()

        for kobj in items:
            item = self.get_db_item(kobj)
            if item:
                self.update(kobj, item)
                updated[item.id] = kobj
            else:
                item = self.add(kobj, kobj.briefy_id)
                created[item.id] = kobj

        self.sync_knack()
        msg = '{model} created: {created} / {model} updated: {updated}'.format(
            model=str(self.model.__name__),
            created=len(created),
            updated=len(updated)
        )
        logger.info(msg)
        return created, updated
