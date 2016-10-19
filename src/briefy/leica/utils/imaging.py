"""Image management functions."""
import logging

logger = logging.getLogger('briefy.leica')
logger.setLevel(logging.INFO)


def __eq__(value1, value2):
    """Compare two values."""
    return value1 == value2


def __ge__(value1, value2):
    """Compare two values."""
    return value1 >= value2


def __le__(value1, value2):
    """Compare two values."""
    return value1 <= value2


def __gt__(value1, value2):
    """Compare two values."""
    return value1 > value2


def __lt__(value1, value2):
    """Compare two values."""
    return value1 < value2

OPERATIONS = {
    'eq': __eq__,
    'min': __ge__,
    'max': __le__,
    'lt': __lt__,
    'gt': __gt__,
}


def _check_dimensions(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image dimensions.

    :param metadata: Image metadata.
    :param value: Constraint value
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


def _check_ratio(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image ratio.

    :param metadata: Image metadata.
    :param value: Constraint value
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('ratio')
    return OPERATIONS[operator](str(value1), str(value))


def _check_size(metadata: dict, value: int, operator: str='eq') -> bool:
    """Check image size.

    :param metadata: Image metadata.
    :param value: Constraint value
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('size')
    return OPERATIONS[operator](int(value1), int(value))


def _check_dpi(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image DPI.

    :param metadata: Image metadata.
    :param value: Constraint value
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('dpi')
    return OPERATIONS[operator](str(value1), str(value))


def _check_mimetype(metadata: dict, value: str, operator: str='eq') -> bool:
    """Check image mimetype.

    :param metadata: Image metadata.
    :param value: Constraint value
    :param operator: Constraint operator
    :return: Boolean indicating if constraint was met or not.
    """
    value1 = metadata.get('mimetype')
    return OPERATIONS[operator](str(value1), str(value))


CHECKERS = {
    'dimensions': _check_dimensions,
    'ratio': _check_ratio,
    'size': _check_size,
    'dpi': _check_dpi,
    'mimetype': _check_mimetype,
}


def check_image_constraints(metadata: dict, constraints: dict) -> list:
    """Check if the constraints are met for Image metadata.

    :param metadata: Image metadata.
    :param constraints: Constraints to be checked.
    :return: List of error messages.
    """
    response = []
    for name, params in constraints.items():
        if 'value' not in params:
            logger.info('Error with constraints format')
            continue

        value = params['value']
        operator = params.get('operator', 'eq')

        if name not in CHECKERS:
            logger.info('Invalid constraint name {name}'.format(name=name))
            continue
        check = CHECKERS[name](metadata, value, operator)
        if not check:
            response.append(
                {
                    'check': name,
                    'text': 'Check for {name} failed'.format(name=name)
                }
            )
    return response
