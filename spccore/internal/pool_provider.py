"""
This module allow us to simplify the logic of any method that can run with either multiple threads or single thread.

To use this wrapper with multiple threads::
    pool = pool_provider.get_pool()
    try:
        pool.map(function, iterable)
    finally:
        pool.terminate()

To use this wrapper for single thread::
    pool = pool_provider.get_pool(size=1)

"""

import multiprocessing
import multiprocessing.dummy


DEFAULT_POOL_SIZE = 8
_single_threaded = False


class SingleThreadPool:
    """
    To use single thread with multiprocessing.dummy.Pool syntax
    """

    def map(self, func, iterable):
        """
        Mocking map in multiprocessing.dummy.Pool for single thread

        :param func: the function to evoke
        :param iterable: the list of arguments to pass to func
        """
        for item in iterable:
            func(item)

    def terminate(self):
        """Mocking terminate in multiprocessing.dummy.Pool for single thread"""
        pass


class FakeLock:
    """Mocking lock in single thread pool"""

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


class SingleValue:
    """Mocking multiprocessing.Value for single thread pool """

    value = None

    def __init__(self, type, value):
        self.value = value

    def get_lock(self):
        """Mocking get_lock in multiprocessing.Value"""
        return FakeLock()


def get_pool(size: int = DEFAULT_POOL_SIZE):
    """
    Return a pool of thread for the given size

    :param size: the number of threads in the pool
    """
    if size is not None and size == 1:
        global _single_threaded
        _single_threaded = True
        return SingleThreadPool()
    elif size is None or size < 1:
        _single_threaded = False
        return multiprocessing.dummy.Pool(DEFAULT_POOL_SIZE)
    else:
        _single_threaded = False
        return multiprocessing.dummy.Pool(size)


def get_value(type, value):
    """To use single thread with multiprocessing.Value syntax"""
    if _single_threaded:
        return SingleValue(type, value)
    else:
        return multiprocessing.Value(type, value)
