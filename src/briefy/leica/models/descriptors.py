"""Custom descriptors to handle get, set and delete of special attributes."""
from briefy.common.db import Base
from uuid import uuid4


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
            if not value.get('id', None):
                fk_id = self.get_or_create_obj_id(obj)
                value[self._fk_attr] = fk_id
                sub_object = self._model(**value)
                session = obj.__session__
                session.add(sub_object)
                # TODO: call obj.some_hook to change something else, like workflow
                # this should be another optional parameter in the init
            else:
                sub_object = self.__get__(obj)
                if sub_object:
                    for k, v in value.items():
                        setattr(sub_object, k, v)
        elif isinstance(value, self._model):
            setattr(obj, self._field_name, value)
        elif not value:
            pass
        else:
            msg = 'Value must be a map to create a new instance or an instance of {model_name}.'
            raise ValueError(msg.format(self._model.__name__))

    def __delete__(self, obj):
        """Remove the related object with soft delete."""
        # TODO: implement a way to delete sub_object
        pass

    def get_or_create_obj_id(self, obj):
        if not obj.id:
            obj.id = uuid4()

        return obj.id


class MultipleRelationshipWrapper(UnaryRelationshipWrapper):
    """Descriptor to wrap set and get values from a multiple relationship."""

    def __set__(self, obj, values) -> None:
        """Set the new instance of the related object.

        :param obj: instance of the model where the descriptor attribute is defined
        :param values: List of items to be created
        :return: None
        """
        sub_objects = []
        session = obj.__session__
        for value in values:
            if isinstance(value, dict):
                if not value.get('id', None):
                    fk_id = self.get_or_create_obj_id(obj)
                    value[self._fk_attr] = fk_id
                    sub_object = self._model(**value)
                    session.add(sub_object)
                    # TODO: call obj.some_hook to change something else, like workflow
                    # this should be another optional parameter in the init
                else:
                    sub_object = self.__get__(obj)
                    if sub_object:
                        for k, v in value.items():
                            setattr(sub_object, k, v)
            elif isinstance(value, self._model):
                sub_objects.append(value)
            elif not value:
                pass
            else:
                msg = 'Value must be a map to create a new instance or an instance of {model_name}.'
                raise ValueError(msg.format(self._model.__name__))
        if sub_objects:
            setattr(obj, self._field_name, sub_objects)
