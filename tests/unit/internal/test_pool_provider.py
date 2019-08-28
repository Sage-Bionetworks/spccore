import pytest
from mock import call, Mock, patch

from multiprocessing.pool import ThreadPool
from multiprocessing.sharedctypes import Synchronized
from spccore.internal.pool_provider import *


# SingleThreadPool
def test_map():
    test_func = Mock()
    pool = SingleThreadPool()
    pool.map(test_func, range(0, 10))
    test_func.assert_has_calls(call(x) for x in range(0, 10))


# SingleThreadPoolProvider
def test_get_pool_for_single_thread_pool():
    assert isinstance(SingleThreadPoolProvider().get_pool(), SingleThreadPool)


def test_get_value_for_single_thread():
    test_value = SingleThreadPoolProvider().get_value('d', 500)
    assert isinstance(test_value, SingleValue)
    test_value.value
    assert test_value.value == 500

    test_value.get_lock()
    test_value.value = 900
    assert test_value.value == 900


# MultipleThreadsPoolProvider
def test_constructor():
    pool_provider = MultipleThreadsPoolProvider(3)
    assert pool_provider.pool_size == 3


def test_constructor_invalid_pool_size():
    with pytest.raises(ValueError):
        MultipleThreadsPoolProvider(-3)


def test_get_pool_for_default_number_of_threads():
    assert isinstance(MultipleThreadsPoolProvider().get_pool(), ThreadPool)


def test_get_pool_for_multiple_thread():
    pool = ThreadPool()
    with patch("multiprocessing.dummy.Pool", return_value=pool) as mock_pool:
        assert pool == MultipleThreadsPoolProvider(3).get_pool()
        mock_pool.assert_called_once_with(3)


# get_value
def test_get_value_for_multiple_thread():
    test_value = MultipleThreadsPoolProvider().get_value('d', 500)
    type(test_value)
    assert isinstance(test_value, Synchronized)
    assert test_value.value == 500

    test_value.get_lock()
    test_value.value = 900
    assert test_value.value == 900
