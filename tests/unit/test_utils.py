import pytest
from spccore.utils import *


def test_validate_type_invalid():
    with pytest.raises(TypeError) as e:
        validate_type(str, 2, "k")
        assert e.message == "k must be of type str."


def test_validate_type_valid():
    validate_type(int, 2, "k")
