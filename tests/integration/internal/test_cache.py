from spccore.internal.cache import *


def test_setup(cache, file_handle_id, file_path):
    exist_file_paths = cache.get_all_unmodified_cached_file_paths(file_handle_id)

    file_path = normalize_path(file_path)
    assert file_path not in exist_file_paths


def test_register_example(cache, file_handle_id, file_path):
    cache.register(file_handle_id, file_path)

    file_path = normalize_path(file_path)
    exist_file_paths = cache.get_all_unmodified_cached_file_paths(file_handle_id)
    assert len(exist_file_paths) == 1
    assert file_path in exist_file_paths


def test_download_default_location_empty_cache(cache, file_handle_id, file_path):
    download_dir = cache.get_cache_dir(file_handle_id)

    # assume that we downloaded the file
    os.makedirs(download_dir)
    download_path = normalize_path(shutil.copy(file_path, download_dir))
    cache.register(file_handle_id, download_path)

    exist_file_paths = cache.get_all_unmodified_cached_file_paths(file_handle_id)
    assert download_path in exist_file_paths


def test_download_default_location_not_empty_cache(cache, file_handle_id, file_path):
    cache.register(file_handle_id, file_path)
    exist_file_paths = cache.get_all_unmodified_cached_file_paths(file_handle_id)

    download_dir = cache.get_cache_dir(file_handle_id)
    download_path = normalize_path(shutil.copy(file_path, download_dir))
    assert download_path not in exist_file_paths

    cache.register(file_handle_id, download_path)

    exist_file_paths = cache.get_all_unmodified_cached_file_paths(file_handle_id)
    assert download_path in exist_file_paths


def test_after_modified(cache, file_handle_id, file_path):
    cache.register(file_handle_id, file_path)
    exist_file_paths = cache.get_all_unmodified_cached_file_paths(file_handle_id)
    assert normalize_path(file_path) in exist_file_paths

    with open(file_path, 'w') as f:
        f.write("some other text")

    exist_file_paths = cache.get_all_unmodified_cached_file_paths(file_handle_id)
    assert len(exist_file_paths) == 0
