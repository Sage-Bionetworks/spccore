import abc
import multiprocessing
import multiprocessing.dummy


DEFAULT_POOL_SIZE = 8


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


class PoolProvider(metaclass=abc.ABCMeta):
    """
    Formal interface for a pool provider.
    """

    @abc.abstractmethod
    def get_pool(self):
        pass

    @abc.abstractmethod
    def get_value(self, type, value):
        pass


class SingleThreadPoolProvider(PoolProvider):

    def get_pool(self):
        return SingleThreadPool()

    def get_value(self, type, value):
        return SingleValue(type, value)


class MultipleThreadsPoolProvider(PoolProvider):

    def __init__(self, pool_size:int = DEFAULT_POOL_SIZE):
        if not pool_size:
            self.pool_size = DEFAULT_POOL_SIZE
        elif pool_size > 1:
            self.pool_size = pool_size
        else:
            raise ValueError("Invalid pool size for MultipleThreadsPoolProvider.")

    def get_pool(self):
        return multiprocessing.dummy.Pool(self.pool_size)

    def get_value(self, type, value):
        return multiprocessing.Value(type, value)
