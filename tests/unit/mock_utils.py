# For Python 3.5, Mock's call list is not ordered
def assert_call_list_equals(expected: list, actual: list):
    assert len(expected) == len(actual)
    for c in expected:
        assert c in actual
