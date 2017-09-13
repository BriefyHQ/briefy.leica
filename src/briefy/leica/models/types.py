"""Custom leica sqlalchemy types."""
from sqlalchemy_utils import TimezoneType as BaseTimezoneType


class TimezoneType(BaseTimezoneType):
    """Custom type to fix issue with timezone values coercion."""

    def _coerce(self, value):
        if value is not None and not isinstance(value, self.python_type):
            if not isinstance(value, str):
                value = str(value)
            obj = self._to(value)
            if obj is None:
                raise ValueError(f"unknown time zone '{value}'")
            return obj
        return value
