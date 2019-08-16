import pytest
from spccore.internal.cache import *


TEST_CACHE_ROOT_DIR = "cache_integration_test"


@pytest.fixture
def cache() -> Cache:
    os.makedirs(TEST_CACHE_ROOT_DIR)
    cache = Cache(cache_root_dir=TEST_CACHE_ROOT_DIR)
    cache.purge(from_epoch_time_to_datetime(time.time()))
    yield cache
    try:
        shutil.rmtree(TEST_CACHE_ROOT_DIR)
    except OSError:
        pass


@pytest.fixture
def file_path() -> str:
    file_name = "test.txt"
    with open(file_name, 'w') as f:
        f.write("some text")
    yield file_name
    try:
        os.remove(file_name)
    except OSError:
        pass


@pytest.fixture
def file_handle_id() -> int:
    return 1234567
