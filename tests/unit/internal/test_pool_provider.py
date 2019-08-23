from mock import call, Mock

from multiprocessing.pool import ThreadPool
from multiprocessing.sharedctypes import Synchronized
from spccore.internal.pool_provider import *


# SingleThreadPool
def test_map():
    test_func = Mock()
    pool = SingleThreadPool()
    pool.map(test_func, range(0, 10))
    test_func.assert_has_calls(call(x) for x in range(0, 10))


# PoolProvider:
def test_get_pool_for_single_thread():
    assert isinstance(get_pool(1), SingleThreadPool)


def test_get_pool_for_default_threads():
    assert isinstance(get_pool(), ThreadPool)


def test_get_pool_for_multiple_thread():
    assert isinstance(get_pool(3), ThreadPool)


# get_value
def test_get_value_for_multiple_thread():
    _ = get_pool()
    test_value = get_value('d', 500)
    type(test_value)
    assert isinstance(test_value, Synchronized)
    assert test_value.value == 500

    test_value.get_lock()
    test_value.value = 900
    assert test_value.value == 900


def test_get_value_for_single_thread():
    _ = get_pool(1)
    test_value = get_value('d', 500)
    assert isinstance(test_value, SingleValue)
    test_value.value
    assert test_value.value == 500

    test_value.get_lock()
    test_value.value = 900
    assert test_value.value == 900
