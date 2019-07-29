import json

from spccore.constants import *
from spccore.utils import *
from .lock import *
from .pathutils import *


class Cache:
    """
    Represent a cache in which files are accessed by file handle ID.
    The cache's design is documented in confluence at
    https://sagebionetworks.jira.com/wiki/spaces/SYNR/pages/34373660/Common+Client+Command+set+and+Cache+C4
    """

    def __init__(self, *, cache_root_dir: str = SYNAPSE_DEFAULT_CACHE_ROOT_DIR) -> None:
        """
        Create an instance of the Cache

        :param cache_root_dir: the root directory of the Synapse cache
        :raises TypeError: when one or more parameters have invalid type
        """
        validate_type(str, cache_root_dir, "cache_root_dir")
        self.cache_root_dir = cache_root_dir

    def get_cache_dir(self, file_handle_id: int) -> str:
        """
        Hash and return the location on the cache that file_handle_id is assigned to

        :param file_handle_id: the file_handle_id to look up
        :return: the location on the cache that file_handle_id is assigned to
        :raises TypeError: when one or more parameters have invalid type
        """
        validate_type(int, file_handle_id, "file_handle_id")

        return os.path.join(self.cache_root_dir,
                            str(file_handle_id % SYNAPSE_DEFAULT_CACHE_BUCKET_SIZE),
                            str(file_handle_id))

    def get_all_unmodified_cached_file_paths(self, file_handle_id: int) -> typing.List[str]:
        """
        Performs a cache Read and retrieve all file paths for the given file handle id from the cache

        :param file_handle_id: the file handle id to look up
        :returns: The paths to the file in the cache if the file exists and has not been modified
        :raises TypeError: when one or more parameters have invalid type
        """
        validate_type(int, file_handle_id, "file_handle_id")

        cache_dir = self.get_cache_dir(file_handle_id)
        if not os.path.exists(cache_dir):
            return []
        return _get_all_non_modified_paths(cache_dir)

    def register(self, file_handle_id: int, file_path: str) -> dict:
        """
        Performs a cache Write to register file_path with file_handle_id in the cache

        :param file_handle_id: the file handle id of the file
        :param file_path: the actual file path
        :return: the cache map
        :raises TypeError: when one or more parameters have invalid type
        """
        validate_type(int, file_handle_id, "file_handle_id")
        validate_type(str, file_path, "file_path")

        if not file_path or not os.path.exists(file_path):
            raise ValueError("Can't find file \"%s\"" % file_path)

        cache_dir = self.get_cache_dir(file_handle_id)
        file_path = normalize_path(file_path)
        modified_time = get_modified_time_in_iso(file_path)

        with Lock(SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME, current_working_directory=cache_dir):
            cache_map = _get_cache_map(cache_dir)
            cache_map[file_path] = modified_time
            _write_cache_map(cache_map, cache_dir)

        return cache_map

    def remove(self, file_handle_id: int, *, file_path: str = None, delete_file: bool = False) -> typing.List[str]:
        """
        Performs a cache Write to remove a file(s) from the cache.

        :param file_handle_id: the file handle id to look up
        :param file_path: the file_path to look up and remove.
            Default None, which will remove all copies found in the cache.
        :param delete_file: Set to True to remove the actual file. Default False.
        :returns: A list of file paths removed
        :raises TypeError: when one or more parameters have invalid type
        """
        validate_type(int, file_handle_id, "file_handle_id")
        removed = []
        cache_dir = self.get_cache_dir(file_handle_id)

        # to keep the critical section minimal, performs operations that does not need to lock prior to acquiring lock
        file_path = normalize_path(file_path)
        if delete_file and file_path and os.path.exists(file_path):
            # if the actual file is deleted and we still keep a ref in the cache, that ref is out of date
            # the cache will continue to work as expected
            os.remove(file_path)
            removed.append(file_path)

        with Lock(SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME, current_working_directory=cache_dir):
            cache_map = _get_cache_map(cache_dir)

            if file_path is None:
                for path in cache_map:
                    if delete_file is True and os.path.exists(path):
                        os.remove(path)
                    removed.append(path)
                cache_map = {}
            elif file_path in cache_map:
                del cache_map[file_path]

            _write_cache_map(cache_map, cache_dir)

        return removed

    def purge(self, before_date: datetime.datetime, *, dry_run: bool = False) -> typing.List[str]:
        """
        Purge the cache. Use with caution. Delete files whose cache maps were last updated prior to the given date.
        Deletes .cacheMap files and files that the cache map point to.

        This function is recommended when working with PHI or sensitive data.

        :param before_date: the cutoff time to look up
        :param dry_run: Set to True to list all cache dir that would be removed without actually deleting the files.
            Default False.
        :return: the list of file paths that has been removed
        :raises TypeError: when one or more parameters have invalid type
        """
        validate_type(datetime.datetime, before_date, "before_date")
        removed = []
        for cache_dir in _cache_dirs(self.cache_root_dir):
            removed.extend(_purge_cache_dir(before_date, cache_dir, dry_run))
        return removed


# Helper methods
# These methods are not designed to be used outside of this module.


def _purge_cache_dir(before_date: datetime.datetime, cache_dir: str, dry_run: bool) -> typing.List[str]:
    """
    Purge a single cache directory and remove all files that are recorded before a set date.

    :param before_date: the cutoff date
    :param cache_dir: the target directory
    :param dry_run: Set to True to return the list of file paths that would be removed without deleting the files.
    :return: a list of file paths that were removed
    """
    removed = []
    remain_map = {}
    with Lock(SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME, current_working_directory=cache_dir):
        cache_map = _get_cache_map(cache_dir)
        for file_path, cache_time in cache_map.items():
            if before_date > from_iso_to_datetime(cache_time):
                if not dry_run and os.path.exists(file_path):
                    os.remove(file_path)
                removed.append(file_path)
            else:
                remain_map[file_path] = cache_time
        if not dry_run:
            if not remain_map:
                shutil.rmtree(cache_dir)
            else:
                _write_cache_map(remain_map, cache_dir)
    return removed


def _get_all_non_modified_paths(cache_dir: str) -> typing.List[str]:
    """
    Perform a cache map read and return all non-modified paths in the given cache directory

    :param cache_dir: the cache directory to look for
    :return: all non-modified paths
    """
    cache_map = _get_cache_map(cache_dir)
    non_modified_paths = []
    for path in cache_map:
        if get_modified_time_in_iso(path) == cache_map.get(path):
            non_modified_paths.append(path)
    return non_modified_paths


def _get_cache_map(cache_dir: str) -> dict:
    """
    Perform a cache map read and return the cache map for a given cache directory

    :param cache_dir: the path to the cache directory
    :return: a dictionary with the cache map of all files in the cache folder
    """
    cache_map_file_path = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)

    if not os.path.exists(cache_map_file_path):
        return {}
    with Lock(SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME, current_working_directory=cache_dir):
        with open(cache_map_file_path, 'r') as f:
            cache_map = json.load(f)
    return cache_map


def _write_cache_map(cache_map: dict, cache_dir: str) -> None:
    """
    Perform a cache map write

    :param cache_map: the map to write
    :param cache_dir: the location to write to
    """
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    cache_map_file = os.path.join(cache_dir, SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME)

    with Lock(SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME, current_working_directory=cache_dir):
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
    cache_map = _get_cache_map(cache_dir)
    cache_time = cache_map.get(normalize_path(file_path))
    return cache_time is None or cache_time == get_modified_time_in_iso(file_path)


def _cache_dirs(cache_root_dir: str) -> typing.List[str]:
    """
    Generate a list of all cache dirs, directories of the form:
    [cache_root_dir]/949/59949
    """
    if not os.path.exists(cache_root_dir):
        return []
    for hashed_dir in os.listdir(cache_root_dir):
        path_to_hashed_dir = os.path.join(cache_root_dir, hashed_dir)
        if os.path.isdir(path_to_hashed_dir) and re.match(r'\d+', hashed_dir):
            for file_handle_id_dir in os.listdir(path_to_hashed_dir):
                path_to_file_handle_id_dir = os.path.join(path_to_hashed_dir, file_handle_id_dir)
                if os.path.isdir(path_to_file_handle_id_dir) and re.match(r'\d+', file_handle_id_dir):
                    yield path_to_file_handle_id_dir


def _get_file_handle_id(cache_dir: str) -> int:
    """
    Extract the file handle id from the given cache directory.
    For example: return 678543 for "<cache_root>/543/678543"

    :param cache_dir: the given cache directory
    :return: the file handle id
    """
    return int(os.path.basename(os.path.normpath(cache_dir)))
