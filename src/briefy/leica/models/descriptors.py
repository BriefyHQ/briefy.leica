"""Custom descriptors to handle get, set and delete of special attributes."""
from briefy.common.db import Base


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
                location = self._model(**value)
                session = obj.__session__
                session.add(location)
                # TODO: call obj.some_hook to change something else, like workflow
                # this should be another optional parameter in the init
            else:
                location = self.__get__(obj)
                if location:
                    for k, v in value.items():
                        setattr(location, k, v)
        elif isinstance(value, self._model):
            setattr(obj, self._field_name, value)
        elif not value:
            pass
        else:
            msg = 'Value must be a map to create a new instance or an instance of {model_name}.'
            raise ValueError(msg.format(self._model.__name__))

    def __delete__(self, obj):
        """Remove the related object with soft delete."""
        # TODO: implement a way to delete the working location
