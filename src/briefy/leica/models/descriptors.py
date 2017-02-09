"""Custom descriptors to handle get, set and delete of special attributes."""
from briefy.common.db import Base
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

    def __get__(self, obj, obj_type=None) -> Base:
        """Get the data from the field.

        :param obj: instance of the model where the descriptor attribute is defined
        :param obj_type: not used
        :return: instance of the related object
        """
        return getattr(obj, self._field_name, None)

    def __set__(self, obj, value) -> None:
        """Set the new instance of the related object.

        :param obj: instance of the model where the descriptor attribute is defined
        :param value: value received to
        :return: None
        """
        if isinstance(value, dict):
            self.create_or_update_sub_object(obj, value)
        elif isinstance(value, self._model):
            setattr(obj, self._field_name, value)
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

    def create_or_update_sub_object(self, obj, value):
        """"Create a new sub object o update an existing instance."""
        if not value.get('id', None):
            self.create_sub_object(obj, value)
        else:
            self.update_sub_object(obj, value)

    def create_sub_object(self, obj, value):
        """Create a new sub object instance."""
        session = object_session(obj)
        if not obj.id or not session:
            # do not try to add a new instance if the obj is not persisted yet.
            return
        fk_id = obj.id
        value[self._fk_attr] = fk_id
        sub_object = self._model(**value)
        session.add(sub_object)

    def update_sub_object(self, obj, value):
        """Update an existing sub object instance."""
        sub_object = self.__get__(obj)
        if sub_object:
            for k, v in value.items():
                setattr(sub_object, k, v)


class MultipleRelationshipWrapper(UnaryRelationshipWrapper):
    """Descriptor to wrap set and get values from a multiple relationship."""

    def __set__(self, obj, values) -> None:
        """Set the new instance of the related object.

        :param obj: instance of the model where the descriptor attribute is defined
        :param values: List of items to be created
        :return: None
        """
        sub_model_instances = []
        for value in values:
            if isinstance(value, dict):
                self.create_or_update_sub_object(obj, value)
            elif isinstance(value, self._model):
                sub_model_instances.append(value)
            elif not value:
                pass
            else:
                self.raise_value_error()
        if sub_model_instances:
            setattr(obj, self._field_name, sub_model_instances)


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
        self._permissions = permission

    def __call__(self, collection, proxy):
        descriptor = LocalRoleProxyDescriptor(
            collection,
            proxy,
            self._permissions
        )
        return descriptor.__get__, descriptor.__set__
