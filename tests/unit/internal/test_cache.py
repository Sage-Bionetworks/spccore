from unittest.mock import patch, call, mock_open

from spccore.internal.cache import *
from spccore.internal.cache import _cache_dirs, _get_modified_time, _normalize_path, _is_modified, _write_cache_map, \
    _get_cache_map, _get_all_non_modified_paths, _get_modified_time_in_iso


# test _cache_dirs
def test_private_cache_dirs_empty():
    with patch.object(os, "listdir", return_value=list()) as mock_listdir:
        dirs = _cache_dirs(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)
        assert len(list(dirs)) == 0
        mock_listdir.assert_called_once_with(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)


def test_private_cache_dirs_with_invalid_dirs():
    with patch.object(os, "listdir", side_effect=[["123", "fake_name", "another1"],
                                                  ["987123", "other", "567123"]]) as mock_listdir, \
            patch.object(os.path, "isdir", return_value=True) as mock_isdir:
        dirs = _cache_dirs(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)
        assert list(dirs) == [os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123"),
                              os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "567123")]
        assert mock_listdir.call_args_list == [call(SYNAPSE_DEFAULT_CACHE_ROOT_DIR),
                                               call(os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123"))]
        assert mock_isdir.call_args_list == [call(os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123")),
                                             call(os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123")),
                                             call(os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "other")),
                                             call(os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "567123")),
                                             call(os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "fake_name")),
                                             call(os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "another1"))]


# test _get_modified_time
def test_private_get_modified_time_with_non_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert _get_modified_time(path) is None
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_not_called()


def test_private_get_modified_time_with_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert _get_modified_time(path) == 1
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_called_once_with(path)


# test _get_modified_time_in_iso
def test_private_get_modified_time_in_iso_with_non_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert _get_modified_time_in_iso(path) is None
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_not_called()


def test_private_get_modified_time_in_iso_with_exist_path():
    path = "some_path"
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert _get_modified_time_in_iso(path) == '1970-01-01T00:00:01.000Z'
        mock_exists.assert_called_once_with(path)
        mock_getmtime.assert_called_once_with(path)


# test _normalize_path
def test_private_normalize_path_with_none():
    with patch.object(os.path, "abspath") as mock_abspath, \
            patch.object(os.path, "normcase") as mock_normcase:
        assert _normalize_path(None) is None
        mock_abspath.assert_not_called()
        mock_normcase.assert_not_called()


def test_private_normalize_path_with_unix_path():
    linux_path = "/home/ubuntu/"
    with patch.object(os.path, "abspath", return_value=linux_path) as mock_abspath, \
            patch.object(os.path, "normcase", return_value=linux_path) as mock_normcase:
        assert _normalize_path(linux_path) == linux_path
        mock_abspath.assert_called_once_with(linux_path)
        mock_normcase.assert_called_once_with(linux_path)


def test_private_normalize_path_with_windows_path():
    windows_path = "C:\\Administrator\\Documents"
    linux_path = "C:/Administrator/Documents"
    with patch.object(os.path, "abspath", return_value=windows_path) as mock_abspath, \
            patch.object(os.path, "normcase", return_value=windows_path) as mock_normcase:
        assert _normalize_path(windows_path) == linux_path
        mock_abspath.assert_called_once_with(windows_path)
        mock_normcase.assert_called_once_with(windows_path)


# test _is_modified
def test_private_is_modified_empty_cache_map():
    path = os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123", "test.txt")
    cache_dir = os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123")
    with patch("spccore.internal.cache._get_cache_map", return_value={}) as mock_get_cache_map, \
            patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
        assert _is_modified(cache_dir, path)
        mock_get_cache_map.assert_called_once_with(cache_dir)
        mock_getmtime.assert_not_called()


# test _write_cache_map
def test_private_write_cache_map_cache_dir_not_exist():
    to_write = {}
    cache_dir = os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123")
    cache_map_file = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch.object(os, "makedirs") as mock_makedirs, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "dump") as mock_json_dump:
        _write_cache_map(to_write, cache_dir)
        mock_exists.assert_called_once_with(cache_dir)
        mock_makedirs.assert_called_once_with(cache_dir)
        mock_file.assert_called_once_with(cache_map_file, 'w')
        mock_json_dump.assert_called_once_with(to_write, mock_file())
        mock_file().write.assert_called_once_with('\n')


def test_private_write_cache_map_cache_dir_exist():
    to_write = {}
    cache_dir = os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123")
    cache_map_file = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch.object(os, "makedirs") as mock_makedirs, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "dump") as mock_json_dump:
        _write_cache_map(to_write, cache_dir)
        mock_exists.assert_called_once_with(cache_dir)
        mock_makedirs.assert_not_called()
        mock_file.assert_called_once_with(cache_map_file, 'w')
        mock_json_dump.assert_called_once_with(to_write, mock_file())
        mock_file().write.assert_called_once_with('\n')


# test _get_cache_map
def test_private_get_cache_map_not_exist():
    cache_dir = os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123")
    cache_file_path = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "load") as mock_json_load:
        assert _get_cache_map(cache_dir) == {}
        mock_exists.assert_called_once_with(cache_file_path)
        mock_file.assert_not_called()
        mock_json_load.assert_not_called()


def test_private_get_cache_map_exist():
    cache_dir = os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123")
    cache_file_path = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "load", return_value={}) as mock_json_load:
        assert _get_cache_map(cache_dir) == {}
        mock_exists.assert_called_once_with(cache_file_path)
        mock_file.assert_called_once_with(cache_file_path, 'r')
        mock_json_load.assert_called_once_with(mock_file())


# test _get_all_non_modified_paths
def test_private_get_all_non_modified_paths():
    cache_dir = os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "123", "987123")
    cache_map = {
        "/some/path/to/file.txt": '2019-07-01T00:00:00.000Z',
        "/some/other/path/to/file2.txt": '2019-07-01T00:03:01.000Z'
    }
    mtimes = ['2019-07-01T00:00:00.001Z', '2019-07-01T00:03:01.000Z']
    with patch("spccore.internal.cache._get_cache_map", return_value=cache_map) as mock_get_cache_map, \
            patch("spccore.internal.cache._get_modified_time_in_iso", side_effect=mtimes) as mock_get_mtime_in_iso:
        assert _get_all_non_modified_paths(cache_dir) == ["/some/other/path/to/file2.txt"]
        mock_get_cache_map.assert_called_once_with(cache_dir)
        assert mock_get_mtime_in_iso.call_args_list == [call("/some/path/to/file.txt"),
                                                        call("/some/other/path/to/file2.txt")]


class TestCache:

    # test constructor
    def test_constructor(self):
        pass

    # test get_default_file_path

    # test get_cached_file_path

    # test get_all_cached_file_path

    # test register

    # test remove

    # test purge
