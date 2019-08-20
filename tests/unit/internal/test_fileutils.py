import os
import pytest

from unittest.mock import patch, Mock, mock_open

from spccore.internal.fileutils import *


@pytest.fixture
def file_setup():
    file_name = "test_fileutils.txt"
    data = os.urandom(200)
    with open(file_name, 'wb') as writer:
        writer.write(data)
    yield file_name, data
    os.remove(file_name)


# round trip test
def test_get_md5_hex_digest_integration(file_setup):
    file_name, data = file_setup
    md5 = hashlib.md5()
    md5.update(data)
    assert md5.hexdigest() == get_md5_hex_digest(file_name, block_size_byte=10)


# unit tests
def test_get_md5_hex_digest_path_does_not_exit():
    file_name = "test_get_md5_hex_digest_path_does_not_exit.txt"
    with pytest.raises(FileNotFoundError):
        get_md5_hex_digest(file_name, block_size_byte=10)


def test_get_md5_hex_digest_mock():
    file_name = "test_get_md5_hex_digest_mock.txt"
    md5 = Mock()
    reader = Mock()
    data = r'abc'
    digest = "a6022ff801a82913d23cdf614b47a69f"
    with patch.object(hashlib, "md5", return_value=md5) as mock_md5, \
            patch.object(md5, "update") as mock_update, \
            patch.object(md5, "hexdigest", return_value=digest) as mock_hexdigest, \
            patch("builtins.open", mock_open(read_data=data)) as mock_file:
        assert digest == get_md5_hex_digest(file_name)
        mock_md5.assert_called_once_with()
        mock_file.assert_called_once_with(file_name, 'rb')
        mock_update.assert_called_once_with(data)
        mock_hexdigest.assert_called_once_with()
