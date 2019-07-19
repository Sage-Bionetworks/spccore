import pytest
from unittest.mock import patch, call, mock_open

from spccore.internal.cache import *
from spccore.internal.cache import _cache_dirs, _is_modified, _write_cache_map, _get_cache_map, _get_file_handle_id, \
    _get_all_non_modified_paths


# test _get_file_handle_id
def test_private_get_file_handle_id(cache_dir, file_handle_id):
    assert _get_file_handle_id(cache_dir) == file_handle_id

# test _cache_dirs
def test_private_cache_dirs_not_exist():
    with patch.object(os, "listdir", return_value=list()) as mock_listdir, \
            patch.object(os.path, "exists", return_value=False) as mock_exists:
        dirs = _cache_dirs(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)
        assert len(list(dirs)) == 0
        mock_listdir.assert_not_called()
        mock_exists.assert_called_once_with(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)


def test_private_cache_dirs_empty():
    with patch.object(os, "listdir", return_value=list()) as mock_listdir, \
            patch.object(os.path, "exists", return_value=True) as mock_exists:
        dirs = _cache_dirs(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)
        assert len(list(dirs)) == 0
        mock_listdir.assert_called_once_with(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)
        mock_exists.assert_called_once_with(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)


def test_private_cache_dirs_with_invalid_dirs():
    with patch.object(os, "listdir", side_effect=[["123", "fake_name", "another1"],
                                                  ["987123", "other", "567123"]]) as mock_listdir, \
            patch.object(os.path, "isdir", return_value=True) as mock_isdir, \
            patch.object(os.path, "exists", return_value=True) as mock_exists:
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
        mock_exists.assert_called_once_with(SYNAPSE_DEFAULT_CACHE_ROOT_DIR)


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
def test_private_write_cache_map_cache_dir_not_exist(cache_dir):
    to_write = {}
    cache_map_file = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch.object(os, "makedirs") as mock_makedirs, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "dump") as mock_json_dump, \
            patch.object(Lock, "blocking_acquire", return_value=True) as mock_lock:
        _write_cache_map(to_write, cache_dir)
        mock_exists.assert_called_once_with(cache_dir)
        mock_makedirs.assert_called_once_with(cache_dir)
        mock_file.assert_called_once_with(cache_map_file, 'w')
        mock_json_dump.assert_called_once_with(to_write, mock_file())
        mock_file().write.assert_called_once_with('\n')
        mock_lock.assert_called_once_with()


def test_private_write_cache_map_cache_dir_exist(cache_dir):
    to_write = {}
    cache_map_file = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch.object(os, "makedirs") as mock_makedirs, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "dump") as mock_json_dump, \
            patch.object(Lock, "blocking_acquire", return_value=True) as mock_lock:
        _write_cache_map(to_write, cache_dir)
        mock_exists.assert_called_once_with(cache_dir)
        mock_makedirs.assert_not_called()
        mock_file.assert_called_once_with(cache_map_file, 'w')
        mock_json_dump.assert_called_once_with(to_write, mock_file())
        mock_file().write.assert_called_once_with('\n')
        mock_lock.assert_called_once_with()


# test _get_cache_map
def test_private_get_cache_map_not_exist(cache_dir):
    cache_file_path = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=False) as mock_exists, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "load") as mock_json_load, \
            patch.object(Lock, "blocking_acquire", return_value=True) as mock_lock:
        assert _get_cache_map(cache_dir) == {}
        mock_exists.assert_called_once_with(cache_file_path)
        mock_file.assert_not_called()
        mock_json_load.assert_not_called()
        mock_lock.assert_not_called()


def test_private_get_cache_map_exist(cache_dir):
    cache_file_path = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)
    with patch.object(os.path, "exists", return_value=True) as mock_exists, \
            patch("builtins.open", mock_open()) as mock_file, \
            patch.object(json, "load", return_value={}) as mock_json_load, \
            patch.object(Lock, "blocking_acquire", return_value=True) as mock_lock:
        assert _get_cache_map(cache_dir) == {}
        mock_exists.assert_called_once_with(cache_file_path)
        mock_file.assert_called_once_with(cache_file_path, 'r')
        mock_json_load.assert_called_once_with(mock_file())
        mock_lock.assert_called_once_with()


# test _get_all_non_modified_paths
def test_private_get_all_non_modified_paths(cache_dir):
    cache_map = {
        "/some/path/to/file.txt": '2019-07-01T00:00:00.000Z',
        "/some/other/path/to/file2.txt": '2019-07-01T00:03:01.000Z'
    }
    mtimes = ['2019-07-01T00:00:00.001Z', '2019-07-01T00:03:01.000Z']
    with patch("spccore.internal.cache._get_cache_map", return_value=cache_map) as mock_get_cache_map, \
            patch("spccore.internal.cache.get_modified_time_in_iso", side_effect=mtimes) as mock_get_mtime_in_iso:
        assert _get_all_non_modified_paths(cache_dir) == ["/some/other/path/to/file2.txt"]
        mock_get_cache_map.assert_called_once_with(cache_dir)
        assert mock_get_mtime_in_iso.call_args_list == [call("/some/path/to/file.txt"),
                                                        call("/some/other/path/to/file2.txt")]


@pytest.fixture
def cache():
    return Cache()


CUSTOM_CACHE_LOCATION = "here"


@pytest.fixture
def custom_cache():
    return Cache(cache_root_dir=CUSTOM_CACHE_LOCATION)


@pytest.fixture
def file_handle_id():
    return 123456


@pytest.fixture
def cache_dir():
    return os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "456", "123456")


@pytest.fixture
def file_path():
    return os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR, "456", "123456", "test.txt")


class TestCache:

    # test constructor
    def test_constructor_with_default_cache_location(self, cache):
        assert cache.cache_root_dir == SYNAPSE_DEFAULT_CACHE_ROOT_DIR

    def test_constructor_with_custom_cache_location(self, custom_cache):
        assert custom_cache.cache_root_dir == CUSTOM_CACHE_LOCATION

    def test_constructor_with_invalid_cache_location(self):
        with pytest.raises(TypeError):
            Cache(cache_root_dir=123)

    # test get_cache_dir
    def test_get_cache_dir_invalid_input_type(self, cache):
        with pytest.raises(TypeError):
            cache.get_cache_dir("123")

    def test_get_cache_dir_with_default_cache(self, cache, file_handle_id):
        assert \
            cache.get_cache_dir(file_handle_id) == os.path.join(SYNAPSE_DEFAULT_CACHE_ROOT_DIR,
                                                                str(file_handle_id % SYNAPSE_DEFAULT_CACHE_BUCKET_SIZE),
                                                                str(file_handle_id))

    def test_get_cache_dir_with_custom_cache(self, custom_cache, file_handle_id):
        assert custom_cache.get_cache_dir(file_handle_id) == \
               os.path.join(CUSTOM_CACHE_LOCATION,
                            str(file_handle_id % SYNAPSE_DEFAULT_CACHE_BUCKET_SIZE),
                            str(file_handle_id))

    # test get_all_unmodified_cached_file_paths
    def test_get_all_unmodified_cached_file_paths_invalid_input_type(self, cache):
        with pytest.raises(TypeError):
            cache.get_all_unmodified_cached_file_paths("123")

    def test_get_all_unmodified_cached_file_paths_cache_dir_not_exists(self, cache, file_handle_id, cache_dir):
        with patch.object(os.path, "exists", return_value=False) as mock_exists, \
             patch("spccore.internal.cache._get_all_non_modified_paths", return_value=list(cache_dir)) as mock_private:
            assert cache.get_all_unmodified_cached_file_paths(file_handle_id) == list()
            mock_exists.assert_called_once_with(cache_dir)
            mock_private.assert_not_called()

    def test_get_all_unmodified_cached_file_paths_cache_dir_exists(self, cache, file_handle_id, cache_dir):
        with patch.object(os.path, "exists", return_value=True) as mock_exists, \
             patch("spccore.internal.cache._get_all_non_modified_paths", return_value=list(cache_dir)) as mock_private:
            assert cache.get_all_unmodified_cached_file_paths(file_handle_id) == list(cache_dir)
            mock_exists.assert_called_once_with(cache_dir)
            mock_private.assert_called_once_with(cache_dir)

    # test register
    def test_register_invalid_file_handle_id_type(self, cache):
        with pytest.raises(TypeError):
            cache.register("123", "test.txt")

    def test_register_invalid_file_path_type(self, cache, file_handle_id):
        with pytest.raises(TypeError):
            cache.register(file_handle_id, 123)

    def test_register_file_path_not_exist(self, cache, file_handle_id, file_path, cache_dir):
        iso_time = '2019-07-01T00:03:01.000Z'
        with pytest.raises(ValueError), \
             patch.object(os.path, "exists", return_value=False) as mock_exists, \
             patch("spccore.internal.cache.Cache.get_cache_dir", return_value=cache_dir) as mock_get_cache_dir, \
             patch("spccore.internal.cache.get_modified_time_in_iso", return_value=iso_time) as mock_get_mtime, \
             patch.object(Lock, "blocking_acquire", return_value=True) as mock_lock, \
             patch("spccore.internal.cache._get_cache_map", return_value={}) as mock_get_cache_map, \
             patch("spccore.internal.cache._write_cache_map") as mock_write_cache_map:
            cache.register(file_handle_id, file_path)
            mock_exists.assert_called_once_with(file_path)
            mock_get_cache_dir.assert_not_called()
            mock_get_mtime.assert_not_called()
            mock_lock.assert_not_called()
            mock_get_cache_map.assert_not_called()
            mock_write_cache_map.assert_not_called()

    def test_register_file_path_exist(self, cache, file_handle_id, file_path, cache_dir):
        iso_time = '2019-07-01T00:03:01.000Z'
        expected_cache_map = {file_path: iso_time}
        with patch.object(os.path, "exists", return_value=True) as mock_exists, \
             patch("spccore.internal.cache.Cache.get_cache_dir", return_value=cache_dir) as mock_get_cache_dir, \
             patch("spccore.internal.cache.get_modified_time_in_iso", return_value=iso_time) as mock_get_mtime, \
             patch.object(Lock, "blocking_acquire", return_value=True) as mock_lock, \
             patch("spccore.internal.cache._get_cache_map", return_value={}) as mock_get_cache_map, \
             patch("spccore.internal.cache._write_cache_map") as mock_write_cache_map:
            assert expected_cache_map == cache.register(file_handle_id, file_path)
            mock_exists.assert_called_once_with(file_path)
            mock_get_cache_dir.assert_called_once_with(file_handle_id)
            mock_get_mtime.assert_called_once_with(normalize_path(file_path))
            mock_lock.assert_called_once_with()
            mock_get_cache_map.assert_called_once_with(cache_dir)
            mock_write_cache_map.assert_called_once_with(expected_cache_map, cache_dir)

    # test remove

    # test purge
