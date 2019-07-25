import typing
from unittest.mock import call


# For Python 3.5, Mock's call list is not ordered
def assert_call_list_equals(expected: typing.List[call], actual: typing.List[call]):
    assert len(expected) == len(actual)
    for c in expected:
        assert c in actual
