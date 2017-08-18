"""Custom descriptors to handle get, set and delete of special attributes."""
from briefy.common.db import Base
from briefy.leica import logger
from sqlalchemy.orm.session import object_session


class UnaryRelationshipWrapper:
    """Descriptor to wrap set and get values from an unary relationship."""

    def __init__(self, field_name: str, model, fk_attr) -> None:
        """Initialize the unary relationship wrapper.

        :param field_name: string with the name of the real relationship field
        :param model: class object of the model to be used as related field
        :param fk_attr: string with the name of the foreign ky attribute to the parent model
        """
        self._model = model
        self._field_name = field_name
        self._fk_attr = fk_attr
        self._attr_created = {}

    def __get__(self, parent_obj, obj_type=None) -> Base:
        """Get the data from the field.

        :param parent_obj: instance of the model where the descriptor attribute is defined
        :param obj_type: not used
        :return: instance of the related object
        """
        value = None
        if parent_obj:
            value = getattr(parent_obj, self._field_name)
            if not value:
                attr_instance_id = self._attr_created.get(parent_obj.id)
                value = self._model.get(attr_instance_id) if attr_instance_id else None
        return value

    def __set__(self, parent_obj, value) -> None:
        """Set the new instance of the related object.

        :param parent_obj: instance of the model where the descriptor attribute is defined
        :param value: value received to
        :return: None
        """
        if isinstance(value, dict):
            self.create_or_update_sub_object(parent_obj, value)
        elif isinstance(value, self._model):
            setattr(parent_obj, self._field_name, value)
        elif not value:
            pass
        else:
            self.raise_value_error()

    def __delete__(self, obj):
        """Remove the related object with soft delete."""
        # TODO: implement a way to delete sub_object
        pass

    def raise_value_error(self):
        """Raise ValueError when value is not dict or model instance."""
        msg = 'Value must be a map to create a new instance or an instance of {model_name}.'
        raise ValueError(msg.format(self._model.__name__))

    def create_or_update_sub_object(self, parent_obj, value):
        """"Create a new sub object o update an existing instance."""
        value_id = value.get('id', None)
        if not value_id:
            self.create_sub_object(parent_obj, value)
        else:
            self.update_sub_object(parent_obj, value)

    def create_sub_object(self, parent_obj, value, collection=None):
        """Create a new sub object instance."""
        field_name = self._field_name
        session = object_session(parent_obj)
        if not parent_obj.id or not session:
            # do not try to add a new instance if the obj is not persisted yet.
            return
        fk_id = parent_obj.id
        value[self._fk_attr] = fk_id
        sub_object = self._model.create(value)
        self._attr_created[str(parent_obj.id)] = sub_object.id
        if collection is not None:
            collection.append(sub_object)
            logger.debug(f'Item appended in collection {sub_object}')
        else:
            setattr(parent_obj, field_name, sub_object)
            logger.debug(f'Attribute {field_name} updated with {sub_object}')

    def update_sub_object(self, obj, values):
        """Update an existing sub object instance."""
        if obj and isinstance(values, dict):
            sub_object = self.__get__(obj)
            if sub_object:
                sub_object.update(values)


class MultipleRelationshipWrapper(UnaryRelationshipWrapper):
    """Descriptor to wrap set and get values from a multiple relationship."""

    def __set__(self, parent_obj, values) -> None:
        """Set the new instance of the related object.

        :param parent_obj: instance of the model where the descriptor attribute is defined
        :param values: List of items to be created
        :return: None
        """
        session = object_session(parent_obj)
        collection = self.__get__(parent_obj) or []
        update_value_ids = []
        update_values = []
        add_values = []

        # get update and add list
        for value in values:
            if isinstance(value, dict):
                value_id = value.get('id', None)
                obj = self._model.get(value_id) if value_id else None
                if not obj:
                    add_values.append(value)
                else:
                    update_value_ids.append(value_id)
                    update_values.append((obj, value))

        # first delete from collection
        if collection:
            delete_ids = [str(item.id) for item in collection
                          if str(item.id) not in update_value_ids]
            for item_id in delete_ids:
                item = self._model.get(item_id)
                collection.remove(item)
                session.delete(item)
                logger.debug(f'Item deleted {item}')

        # update items in collection
        for obj, value in update_values:
            obj.update(value)

        # add new items
        for value in add_values:
            self.create_sub_object(parent_obj, value, collection)

        if session:
            session.flush()


class LocalRoleProxyDescriptor:
    """Descriptor to wrap set and get values from an unary relationship."""

    def __init__(self, collection, proxy, permissions) -> None:
        """Initialize the unary relationship wrapper.

        :param field_name: string with the name of the real relationship field
        :param model: class object of the model to be used as related field
        :param fk_attr: string with the name of the foreign ky attribute to the parent model
        """
        self._collection = collection
        self._proxy = proxy
        self._permissions = permissions

    def __get__(self, obj, obj_type=None) -> Base:
        """Get the data from the field.

        :param obj: instance of the model where the descriptor attribute is defined
        :param obj_type: not used
        :return: instance of the related object
        """
        attr = self._proxy.value_attr
        if obj and attr:
            session = obj.__session__
            if obj not in session.deleted:
                return getattr(obj, attr)

    def __set__(self, obj, value) -> None:
        """Set the new instance of the related object.

        :param obj: instance of the model where the descriptor attribute is defined
        :param value: value received to
        :return: None
        """
        if value is None and obj:
            session = obj.__session__
            session.delete(obj)

        if value and obj:
            attr = self._proxy.value_attr
            setattr(obj, attr, value)

    def __delete__(self, obj):
        """Remove the related object with soft delete."""
        # TODO: implement a way to delete sub_object
        pass


class LocalRolesGetSetFactory:
    """Factory that return get and set functions to the AssociationProxy."""

    def __init__(self, permission):
        """Initialize LocalRolesGetSetFactory."""
        self._permissions = permission

    def __call__(self, collection, proxy):
        """Create a new descriptor instance and return the set and get functions."""
        descriptor = LocalRoleProxyDescriptor(
            collection,
            proxy,
            self._permissions
        )
        return descriptor.__get__, descriptor.__set__
