import pytest

from unittest.mock import patch, Mock, mock_open
from spccore.internal.fileutils import *


def test_get_md5_hex_digest_for_file_path_does_not_exist():
    file_name = "test_get_md5_hex_digest_path_does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        get_md5_hex_digest_for_file(file_name, block_size_byte=10)


def test_get_md5_hex_digest_for_file_mock():
    file_name = "test_get_md5_hex_digest_mock.txt"
    md5 = Mock()
    data = r'abc'
    digest = "a6022ff801a82913d23cdf614b47a69f"
    with patch.object(hashlib, "md5", return_value=md5) as mock_md5, \
            patch.object(md5, "update") as mock_update, \
            patch.object(md5, "hexdigest", return_value=digest) as mock_hexdigest, \
            patch("builtins.open", mock_open(read_data=data)) as mock_file:
        assert digest == get_md5_hex_digest_for_file(file_name)
        mock_md5.assert_called_once_with()
        mock_file.assert_called_once_with(file_name, 'rb')
        mock_update.assert_called_once_with(data)
        mock_hexdigest.assert_called_once_with()


def test_get_md5_hex_digest_for_bytes_mock():
    md5 = Mock()
    data = b'abc'
    digest = "a6022ff801a82913d23cdf614b47a69f"
    with patch.object(hashlib, "md5", return_value=md5) as mock_md5, \
            patch.object(md5, "update") as mock_update, \
            patch.object(md5, "hexdigest", return_value=digest) as mock_hexdigest:
        assert digest == get_md5_hex_digest_for_bytes(data)
        mock_md5.assert_called_once_with()
        mock_update.assert_called_once_with(data)
        mock_hexdigest.assert_called_once_with()


def test_get_part_data_file_path_does_not_exist():
    file_name = "test_get_md5_hex_digest_path_does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        get_part_data(file_name, 1, 100)


def test_get_part_data():
    file_name = "test_get_md5_hex_digest_mock.txt"
    data = r'abc'
    with patch("builtins.open", mock_open(read_data=data)) as mock_file:
        assert data == get_part_data(file_name, 1, 100)
        mock_file.assert_called_once_with(file_name, 'rb')
        mock_file().seek.assert_called_once_with(0)
        mock_file().read.assert_called_once_with(100)
