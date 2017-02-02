"""Custom descriptors to handle get, set and delete of special attributes."""
from briefy.common.db import Base
from uuid import uuid4

from time import sleep


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
        # TODO: HACK: To avoid a race condition when a new object is not committed
        # to the database yet.
        from briefy.leica.models import Order, Professional
        if isinstance(obj, (Order, Professional)):
            sleep(0.5)
        ##########################################################################

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

    @staticmethod
    def get_or_create_obj_id(obj):
        """Return the obj ID or create a new one."""
        if not obj.id:
            obj.id = uuid4()
        return obj.id

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
        session = obj.__session__
        fk_id = self.get_or_create_obj_id(obj)
        value[self._fk_attr] = fk_id
        sub_object = self._model(**value)
        session.add(sub_object)
        # TODO:
        # call obj.some_hook to change something else, like workflow
        # this could be another optional parameter in the init

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
