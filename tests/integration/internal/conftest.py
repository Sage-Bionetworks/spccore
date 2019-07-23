import pytest
from spccore.internal.cache import *


TEST_CACHE_ROOT_DIR = "cache_integration_test"


@pytest.fixture
def cache() -> Cache:
    os.makedirs(TEST_CACHE_ROOT_DIR)
    cache = Cache()
    cache.purge(from_epoch_time_to_datetime(time.time()))
    yield cache
    cache.purge(from_epoch_time_to_datetime(time.time()))
    shutil.rmtree(TEST_CACHE_ROOT_DIR)


@pytest.fixture
def file_path() -> str:
    file_name = "test.txt"
    with open(file_name, 'w') as f:
        f.write("some text")
    yield file_name
    os.remove(file_name)


@pytest.fixture
def file_handle_id() -> int:
    return 1234567
