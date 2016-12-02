"""Test transitions utilities."""
from briefy.leica.utils import transitions
from datetime import datetime

import pytest


class DummyObject:
    """Dummy object."""

    state_history = ()

    def __init__(self, state_history: list):
        """Initialize this object."""
        self.state_history = state_history


_history = [
    {'date': datetime(2016, 12, 21, 12, 0, 0), 'transition': 'create'},
    {'date': datetime(2016, 12, 21, 12, 5, 0), 'transition': 'submit'},
    {'date': datetime(2016, 12, 21, 12, 10, 0), 'transition': 'assign'},
    {'date': datetime(2016, 12, 21, 13, 10, 0), 'transition': 'unassign'},
    {'date': datetime(2016, 12, 21, 14, 10, 0), 'transition': 'assign'},
]

testdata = [
    (['create', ], _history, False, datetime(2016, 12, 21, 12, 0, 0)),
    (['submit', ], _history, False, datetime(2016, 12, 21, 12, 5, 0)),
    (['assign', ], _history, False, datetime(2016, 12, 21, 14, 10, 0)),
    (['assign', ], _history, True, datetime(2016, 12, 21, 12, 10, 0)),
    (['unassign', ], _history, False, datetime(2016, 12, 21, 13, 10, 0)),
    (['assign', 'unassign', ], _history, False, datetime(2016, 12, 21, 14, 10, 0)),
    (['assign', 'unassign', ], _history, True, datetime(2016, 12, 21, 12, 10, 0)),
    (['approve', ], _history, False, None),
]


@pytest.mark.parametrize("t,history,first,expected", testdata)
def test_get_transition_date(t, history, first, expected):
    """Test get_transition_date."""
    func = transitions.get_transition_date
    obj = DummyObject(history)

    assert func(t, obj, first) == expected
