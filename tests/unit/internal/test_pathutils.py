from unittest.mock import patch

from spccore.internal.pathutils import *


# test get_modified_time
def test_get_modified_time_with_non_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert get_modified_time(path) is None
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_not_called()


def test_get_modified_time_with_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert get_modified_time(path) == 1
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_called_once_with(path)


# test get_modified_time_in_iso
def test_get_modified_time_in_iso_with_non_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert get_modified_time_in_iso(path) is None
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_not_called()


def test_get_modified_time_in_iso_with_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert get_modified_time_in_iso(path) == '1970-01-01T00:00:01.000Z'
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_called_once_with(path)


# test normalize_path
def test_normalize_path_with_none():
    with patch.object(os.path, "abspath") as mock_abspath, \
            patch.object(os.path, "normcase") as mock_normcase:
        assert normalize_path(None) is None
        mock_abspath.assert_not_called()
        mock_normcase.assert_not_called()


def test_normalize_path_with_unix_path():
    linux_path = "/home/ubuntu/"
    with patch.object(os.path, "abspath", return_value=linux_path) as mock_abspath, \
            patch.object(os.path, "normcase", return_value=linux_path) as mock_normcase:
        assert normalize_path(linux_path) == linux_path
        mock_abspath.assert_called_once_with(linux_path)
        mock_normcase.assert_called_once_with(linux_path)


def test_normalize_path_with_windows_path():
    windows_path = "C:\\Administrator\\Documents"
    linux_path = "C:/Administrator/Documents"
    with patch.object(os.path, "abspath", return_value=windows_path) as mock_abspath, \
            patch.object(os.path, "normcase", return_value=windows_path) as mock_normcase:
        assert normalize_path(windows_path) == linux_path
        mock_abspath.assert_called_once_with(windows_path)
        mock_normcase.assert_called_once_with(windows_path)
