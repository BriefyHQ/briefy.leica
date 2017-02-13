"""Image management functions."""
from typing import Any

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def __eq__(value1: Any, value2: Any) -> bool:
    """Compare if value1 and value2 are equal."""
    return value1 == value2


def __ge__(value1: Any, value2: Any) -> bool:
    """Compare if value1 is equal or bigger than value2."""
    return value1 >= value2


def __le__(value1: Any, value2: Any) -> bool:
    """Compare if value1 is equal or lower than value2."""
    return value1 <= value2


def __gt__(value1: Any, value2: Any) -> bool:
    """Compare if value1 is bigger than value2."""
    return value1 > value2


def __lt__(value1: Any, value2: Any) -> bool:
    """Compare if value1 is lower than value2."""
    return value1 < value2


def __contains__(value1: Any, value2: Any) -> bool:
    """Check if value1 is in value2."""
    return value1 in value2


OPERATIONS = {
    'eq': __eq__,
    'min': __ge__,
    'max': __le__,
    'lt': __lt__,
    'gt': __gt__,
    'in': __contains__,
}


def _check_dimensions(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image dimensions.

    :param metadata: Image metadata.
    :param value: Constraint value.
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    cw, ch = value.split('x')
    dimensions = metadata.get('dimensions', '')
    w, h = dimensions.split(' x ')
    value1 = (int(w), int(h))
    value2 = (int(cw), int(ch))
    status = OPERATIONS[operator](value1, value2)
    return status


def _check_ratio(metadata: dict, value: float, operator: str='eq') -> bool:
    """Check image ratio.

    :param metadata: Image metadata.
    :param value: Constraint value.
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    dimensions = metadata.get('dimensions', '')
    w, h = dimensions.split(' x ')
    value1 = int(w) / int(h)
    if isinstance(value1, (int, float)):
        value1 = '{0:.2f}'.format(value1)
    value = '{0:.2f}'.format(value)
    return OPERATIONS[operator](str(value1), value)


def _check_size(metadata: dict, value: int, operator: str='eq') -> bool:
    """Check image size.

    :param metadata: Image metadata.
    :param value: Constraint value.
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('size')
    return OPERATIONS[operator](int(value1), int(value))


def _check_dpi(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image DPI.

    :param metadata: Image metadata.
    :param value: Constraint value.
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('dpi')
    return OPERATIONS[operator](str(value1), str(value))


def _check_mimetype(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image mimetype.

    :param metadata: Image metadata.
    :param value: Constraint value.
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('mimetype')
    return OPERATIONS[operator](str(value1), value)


def _check_orientation(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image orientation.

    :param metadata: Image metadata.
    :param value: Constraint value.
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('orientation')
    return OPERATIONS[operator](str(value1), str(value))


CHECKERS = {
    'dimensions': _check_dimensions,
    'ratio': _check_ratio,
    'size': _check_size,
    'dpi': _check_dpi,
    'mimetype': _check_mimetype,
    'orientation': _check_orientation,
}


def check_image_constraints(metadata: dict, constraints: dict) -> list:
    """Check if the constraints are met for Image metadata.

    :param metadata: Image metadata.
    :param constraints: Constraints to be checked.
    :return: List of error messages.
    """
    response = []
    if 'asset' in constraints:
        constraints = constraints['asset']
        if not constraints:
            return response
    for name, checks in constraints.items():
        if isinstance(checks, dict):
            checks = [checks, ]

        for check in checks:
            if 'value' not in check:
                logger.info('Error with constraints format')
                continue
            elif name not in CHECKERS:
                logger.info('Invalid constraint name {name}'.format(name=name))
                continue

            value = check['value']
            operator = check.get('operator', 'eq')

            passed = CHECKERS[name](metadata, value, operator)
            if not passed:
                value = metadata.get(name, '')
                if name == 'ratio':
                    value = ''
                response.append(
                    {
                        'check': name,
                        'text': '{name} check failed {value}'.format(
                            name=name.title(),
                            value=value
                        ).strip()
                    }
                )
    return response
