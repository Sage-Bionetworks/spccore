import math
import json
import re

from spccore.constants import *
from spccore.utils import *
from .lock import *
from .timeutils import *


class Cache:
    """
    Represent a cache in which files are accessed by file handle ID.
    The cache's design is documented in confluence at
    https://sagebionetworks.jira.com/wiki/spaces/SYNR/pages/34373660/Common+Client+Command+set+and+Cache+C4

    Example::

        import spccore.internal.cache

        cache = new spccore.internal.cache.Cache()

        # Download example
        ###################

        file_handle_id = 3
        file_name = "my_test_download_file.txt"
        download_path = "path/to/my_test_upload_file.txt"

        # To optimize download, we consider the following:
        # do we have this file downloaded and has not been modified?
        # was the downloaded file at the download location?

        file_paths = cache.get_all_cached_file_paths(file_handle_id)

        if file_paths is None:
            # do download file to download_path
            cache.register(file_handle_id, download_path)
        else if download_path not in file_paths:
            # copy file from file_paths[0] to download_path
            cache.register(file_handle_id, download_path)


        # Upload example without file_handle_id
        ########################################

        file_name = "my_test_upload_file.txt"
        file_path = "path/to/my_test_upload_file.txt"

        # file_handle_id = result of uploading file at file_path

        cache.register(file_handle_id, file_path)


        # Upload example with file_handle_id and potential modification
        ################################################################

        file_handle_id = 3
        file_name = "my_test_upload_file.txt"
        file_path = "path/to/my_test_upload_file.txt"
        cached_file_path = cache.get_cached_file_path(file_handle_id, file_name, file_path=file_path)

        if cached_file_path is None:
            # new_file_handle_id = result of uploading file at file_path
            cache.register(new_file_handle_id, file_path)

    """

    def __init__(self, *, cache_root_dir: str = SYNAPSE_DEFAULT_CACHE_ROOT_DIR):
        """
        Create an instance of the Cache

        :param cache_root_dir: the root directory of the Synapse cache
        """
        validate_type(str, cache_root_dir, "cache_root_dir")
        self.cache_root_dir = cache_root_dir

    def _get_cache_dir(self, file_handle_id: int) -> str:
        """
        Hash and return the location on the cache that file_handle_id is assigned to

        :param file_handle_id: the file_handle_id to look up
        :return: the location on the cache that file_handle_id is assigned to
        """
        validate_type(int, file_handle_id, "file_handle_id")

        return os.path.join(self.cache_root_dir,
                            str(file_handle_id % SYNAPSE_DEFAULT_CACHE_BUCKET_SIZE),
                            str(file_handle_id))

    def get_default_file_path(self, file_handle_id: int, file_name: str) -> str:
        """
        Lookup a file for the given file handle id using the cache default location

        :param file_handle_id: the file handle id to look up
        :param file_name: the name of the file to look up
        :returns: The path to the file in the cache regardless if the file exists and if it has been modified
        """
        validate_type(int, file_handle_id, "file_handle_id")
        validate_type(str, file_name, "file_name")

        cache_dir = self._get_cache_dir(file_handle_id)
        file_path = os.path.join(cache_dir, file_name)
        return os.path.abspath(file_path)

    def get_cached_file_path(self,
                             file_handle_id: int,
                             file_name: str,
                             *,
                             file_path: str = None
                             ) -> typing.Union[str, None]:
        """
        Retrieve a file for the given file handle id from the cache

        :param file_handle_id: the file handle id to look up
        :param file_name: the file_name to look up
        :param file_path: the file to look up. Default None, which will use the cache default file path.
        :returns: The path to the file in the cache if the file exists and has not been modified
        """
        validate_type(int, file_handle_id, "file_handle_id")
        validate_type(str, file_name, "file_name")

        cache_dir = self._get_cache_dir(file_handle_id)
        if not os.path.exists(cache_dir):
            return None
        if file_path is None:
            file_path = self.get_default_file_path(file_handle_id, file_name)
        if os.path.exists(file_path) and not _is_modified(cache_dir, file_path):
            return os.path.abspath(file_path)
        return None

    def get_all_cached_file_path(self, file_handle_id: int) -> list:
        """
        Retrieve all file paths for the given file handle id from the cache

        :param file_handle_id: the file handle id to look up
        :returns: The paths to the file in the cache if the file exists and has not been modified
        """
        validate_type(int, file_handle_id, "file_handle_id")

        cache_dir = self._get_cache_dir(file_handle_id)
        if not os.path.exists(cache_dir):
            return list()
        return _get_all_non_modified_paths(cache_dir)

    def register(self, file_handle_id: int, file_path: str) -> dict:
        """
        Register file_path with file_handle_id in the cache

        :param file_handle_id: the file handle id of the file
        :param file_path: the actual file path
        :return: the cache map
        """
        validate_type(int, file_handle_id, "file_handle_id")
        validate_type(str, file_path, "file_path")

        if not file_path or not os.path.exists(file_path):
            raise ValueError("Can't find file \"%s\"" % file_path)

        cache_dir = self._get_cache_dir(file_handle_id)
        with Lock(SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME, current_working_directory=cache_dir):
            cache_map = _get_cache_map_at(cache_dir)
            file_path = _normalize_path(file_path)
            cache_map[file_path] = from_epoch_time_to_iso(math.floor(_get_modified_time(file_path)))
            _write_cache_map_to(cache_map, cache_dir)

        return cache_map

    def remove(self, file_handle_id: int, *, file_path: str = None, delete_file: bool = False) -> list:
        """
        Remove a file(s) from the cache.

        :param file_handle_id: the file handle id to look up
        :param file_path: the file_path to look up and remove.
            Default None, which will remove all copies found in the cache.
        :param delete_file: Set to True to remove the actual file. Default False.

        :returns: A list of files removed from the cache.
        """
        validate_type(int, file_handle_id, "file_handle_id")
        removed = []
        cache_dir = self._get_cache_dir(file_handle_id)

        with Lock(SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME, current_working_directory=cache_dir):
            cache_map = _get_cache_map_at(cache_dir)

            if file_path is None:
                for path in cache_map:
                    if delete_file is True and os.path.exists(path):
                        os.remove(path)
                    removed.append(path)
                cache_map = {}
            else:
                file_path = _normalize_path(file_path)
                if file_path in cache_map:
                    if delete_file is True and os.path.exists(file_path):
                        os.remove(file_path)
                    del cache_map[file_path]
                    removed.append(file_path)

            _write_cache_map_to(cache_map, cache_dir)

        return removed

    def purge(self, before_date: datetime.datetime, *, dry_run: bool = False) -> int:
        """
        Purge the cache. Use with caution. Delete files whose cache maps were last updated prior to the given date.
        Deletes .cacheMap files and files stored in the cache.cache_root_dir, but does not delete files stored outside
        the cache.

        :param before_date: the cutoff time to look up
        :param dry_run: Set to True to list all cache dir that would be removed. Default False.
        :return: the number of file handle id directories that has been removed
        """
        before_date = from_datetime_to_epoch_time(before_date)
        count = 0
        for cache_dir in _cache_dirs(self.cache_root_dir):
            # _get_modified_time returns None if the cache map file doesn't exist.
            # We are going to purge directories in the cache that have no .cacheMap file.
            last_modified_time = _get_modified_time(os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME))
            if last_modified_time is None or before_date > last_modified_time:
                if dry_run:
                    print(cache_dir)
                else:
                    shutil.rmtree(cache_dir)
                count += 1
        return count

# Helper methods


def _get_all_non_modified_paths(cache_dir: str) -> list:
    """
    Perform a cache map read and return all non-modified paths in the given cache directory

    :param cache_dir: the cache directory to look for
    :return: all non-modified paths
    """
    cache_map = _get_cache_map_at(cache_dir)
    non_modified_paths = list()
    for path in cache_map:
        normalized_path = _normalize_path(path)
        if _get_modified_time(normalized_path) == cache_map.get(normalized_path):
            non_modified_paths.append(normalized_path)
    return non_modified_paths


def _get_cache_map_at(cache_folder_path: str) -> dict:
    """
    Perform a cache map read and return the cache map for a given cache folder

    :param cache_folder_path: the path to the cache folder
    :return: a dictionary with the cache map of all files in the cache folder
    """
    cache_map_file_path = os.path.join(cache_folder_path, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)

    if not os.path.exists(cache_map_file_path):
        return {}

    with open(cache_map_file_path, 'r') as f:
        cache_map = json.load(f)
    return cache_map


def _write_cache_map_to(cache_map: dict, cache_dir: str) -> None:
    """
    Perform a cache map write

    :param cache_map: the map to write
    :param cache_dir: the location to write to
    """
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    cache_map_file = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)

    with open(cache_map_file, 'w') as f:
        json.dump(cache_map, f)
        f.write('\n')  # For compatibility with R's JSON parser


def _is_modified(cache_dir: str, file_path: str) -> bool:
    """
    Perform a cache map read and check if a file in the cache has been modified

    :param cache_dir: the cache directory
    :param file_path: the file to check
    :return: true if the file's modified time is later than the cache time; false otherwise
    """
    cache_map = _get_cache_map_at(cache_dir)
    cache_time = cache_map.get(_normalize_path(file_path))
    return cache_time < os.path.getmtime(file_path)


# To be compatible with R
def _normalize_path(path: str) -> typing.Union[str, None]:
    """Transforms a path into an absolute path with forward slashes only."""
    if path is None:
        return None
    return re.sub(r'\\', '/', os.path.normcase(os.path.abspath(path)))


def _get_modified_time(path: str) -> typing.Union[int, None]:
    """Return the last modified time of a file / folder identified by path"""
    if os.path.exists(path):
        return os.path.getmtime(path)
    return None


def _cache_dirs(cache_root_dir: str) -> list:
    """
    Generate a list of all cache dirs, directories of the form:
    [cache_root_dir]/949/59949
    """
    for hashed_dir in os.listdir(cache_root_dir):
        path_to_hashed_dir = os.path.join(cache_root_dir, hashed_dir)
        if os.path.isdir(path_to_hashed_dir) and re.match(r'\d+', hashed_dir):
            for file_handle_id_dir in os.listdir(path_to_hashed_dir):
                path_to_file_handle_id_dir = os.path.join(path_to_hashed_dir, file_handle_id_dir)
                if os.path.isdir(path_to_file_handle_id_dir) and re.match(r'\d+', file_handle_id_dir):
                    yield path_to_file_handle_id_dir
