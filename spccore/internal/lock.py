import errno
import os
import shutil

from spccore.internal.timeutils import *
from spccore.internal.dozer import *

"""
An implementation of a lock system that use the os file system as a single semaphore.

In this implementation, to acquire a lock, we attempt to create a file in the os file system. The os will ensure that
only one file is created at a time. To release a lock, we attempt to remove the file.

Example::
    user1_lock = Lock("foo", max_age=datetime.timedelta(seconds=5))
    user2_lock = Lock("foo", max_age=datetime.timedelta(seconds=5))

    # in one thread
    with user1_lock:
        // do something

    # in another thread
    with user2_lock:
        // do something else

Since both user1 and user2 are using the same lock "foo", while user1 is holding the lock, the user2 will wait.
Therefore, {do something} and {do something else} will be executed in sequential.
"""

LOCK_DEFAULT_MAX_AGE = datetime.timedelta(seconds=10)
DEFAULT_BLOCKING_TIMEOUT = datetime.timedelta(seconds=70)
CACHE_UNLOCK_WAIT_TIME_SEC = 0.5
LOCK_FILE_SUFFIX = 'lock'


class LockException(Exception):
    pass


class Lock(object):
    """
    Implements a lock by making a directory named <lock_name>.lock

    Notes: There is no cross-platform, atomic OS operation that both checks whether a file exists and creates the file.
    However, the directory creation OS operation is atomic across platforms. Therefore we use a directory rather than
    a file as the semaphore to lock file access.
    """

    def __init__(self,
                 name: str,
                 *,
                 current_working_directory: str = None,
                 max_age: datetime.timedelta = LOCK_DEFAULT_MAX_AGE,
                 default_blocking_timeout: datetime.timedelta = DEFAULT_BLOCKING_TIMEOUT
                 ) -> None:
        """
        :param name: the name of the lock. It will be used to construct the lock directory name.
        :param current_working_directory: the parent directory of the lock.
        :param max_age: the max time one thread can hold a lock.
        :param default_blocking_timeout: the time one thread will wait and try to acquire the lock.
        """
        self.name = name
        self.last_updated_time = None
        self.current_working_directory = current_working_directory if current_working_directory else os.getcwd()
        self.lock_dir_path = os.path.join(self.current_working_directory, ".".join([name, LOCK_FILE_SUFFIX]))
        self.max_age = max_age
        self.default_blocking_timeout = default_blocking_timeout

    def blocking_acquire(self, *, timeout: datetime.timedelta = None, break_old_locks: bool = True) -> bool:
        """
        Acquire a lock.

        :param timeout: the time frame to acquire the lock.
            If none is set, this function will use the default_blocking_timeout.
        :param break_old_locks: set to False to ignore old locks. Default True.
        :return: True on success; otherwise throws a LockedException.
        :raises LockedException: when it fails to acquire a lock.
        """
        if timeout is None:
            timeout = self.default_blocking_timeout
        try_lock_start_time = time.time()
        while time.time() - try_lock_start_time < timeout.total_seconds():
            if self._acquire_lock(break_old_locks=break_old_locks):
                return True
            else:
                doze(CACHE_UNLOCK_WAIT_TIME_SEC)
        raise LockException("Could not obtain a lock on the file cache within timeout: {timeout}."
                            " Please try again later.".format(**{'timeout': str(timeout)}))

    def release(self) -> None:
        """
        Release lock or do nothing if lock is not held

        :raises OSError: when it fails to release a lock
        """
        if self._has_lock():
            try:
                shutil.rmtree(self.lock_dir_path)
            except OSError as err:
                if err.errno != errno.ENOENT:
                    raise

    def renew(self) -> bool:
        """
        Renew the holding lock by touching the lock file.

        :return: True for success; otherwise False.
        """
        if self._has_lock() and self._get_age() < self.max_age.total_seconds():
            try:
                self._update_lock_time()
                return True
            except OSError:
                return False
        return False

    def _has_lock(self) -> bool:
        """
        Return True if this thread has the lock
        """
        if self.last_updated_time is None:
            return False
        try:
            lock_time = from_epoch_time_to_iso(os.path.getmtime(self.lock_dir_path))
            return lock_time == self.last_updated_time
        except OSError:
            return False

    def _get_age(self) -> int:
        """
        Return the age of the lock

        :raises OSError: when it fails to retrieve the lock's age
        """
        try:
            return time.time() - os.path.getmtime(self.lock_dir_path)
        except OSError as err:
            if err.errno != errno.ENOENT and err.errno != errno.EACCES:
                raise
        return 0

    def _acquire_lock(self, *, break_old_locks: bool = True) -> bool:
        """
        Attempt to acquire lock.

        :param break_old_locks: set to False to ignore old locks. Default True.
        :return: True on success; otherwise False.
        :raises OSError: when it fails to acquire a lock
        """
        if self.renew():
            return True
        try:
            os.makedirs(self.lock_dir_path)
            self._update_lock_time()
        except OSError as err:
            if err.errno != errno.EEXIST and err.errno != errno.EACCES:
                raise
            # already locked by another thread
            if break_old_locks and self._get_age() > self.max_age.total_seconds():
                self._update_lock_time()
            else:
                return False
        return self._has_lock()

    def _update_lock_time(self):
        """
        Update the lock time of the given lock

        :param lock: the Lock object to update
        """
        # sleep for 1 millisecond to make sure that we have a different timestamp
        time.sleep(0.001)
        update_time = time.time()
        os.utime(self.lock_dir_path, (0, update_time))
        self.last_updated_time = from_epoch_time_to_iso(update_time)

    # Make the lock object a Context Manager
    def __enter__(self):
        """
        Important notes:

        We implemented __enter__ to support using lock with the context manager syntax:

        with Lock("foo"):
            <do something while holding the lock>

        However, using nested context manager for the same lock will cause the inner context manager to release the lock
        before the outer context manager does. For example:

        with Lock("foo"):
            <command 1>
            with Lock("foo"):
                <command 2>
            <command 3>

        In the code above, <command 1> and <command 2> was executed while holding lock "foo". When <command 3> is
        reached, the lock "foo" is released by the inner context manager. This usage of the lock context manager is
        confusing to the reader and should be avoided.

        :return: the reference to the lock that can be used to renew the lock.
        """
        self.blocking_acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()
