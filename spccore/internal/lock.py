import errno
import os
import shutil
import datetime

from spccore.internal.dozer import *

"""
An implementation of a lock system that use the os file system as a single semaphore.

In this implementation, to acquire a lock, we attempt to create a file in the os file system. The os will ensure that
only one file is created at a time. To release a lock, we attempt to remove the file.

Example::
    user1_lock = Lock("foo", max_age=datetime.timedelta(seconds=5))
    user2_lock = Lock("foo", max_age=datetime.timedelta(seconds=5))
    
    with user1_lock:
        // do something
    
    with user2_lock:
        // do something else
        
Since both user1 and user2 are using the same lock "foo", while user1 is holding the lock, the user2 will wait.
Therefore, {do something} and {do something else} will be executed in sequential.
"""

LOCK_DEFAULT_MAX_AGE = datetime.timedelta(seconds=10)
DEFAULT_BLOCKING_TIMEOUT = datetime.timedelta(seconds=70)
CACHE_UNLOCK_WAIT_TIME = 0.5


class LockedException(Exception):
    pass


class Lock(object):
    """
    Implements a lock by making a directory named <lock_name>.lock
    """
    SUFFIX = 'lock'

    def __init__(self,
                 name: str,
                 *,
                 current_working_directory: str = None,
                 max_age: datetime.timedelta = LOCK_DEFAULT_MAX_AGE,
                 default_blocking_timeout: datetime.timedelta = DEFAULT_BLOCKING_TIMEOUT
                 ) -> None:
        self.name = name
        self.held = False
        self.current_working_directory = current_working_directory if current_working_directory else os.getcwd()
        self.lock_dir_path = os.path.join(self.current_working_directory, ".".join([name, Lock.SUFFIX]))
        self.max_age = max_age
        self.default_blocking_timeout = default_blocking_timeout

    def blocking_acquire(self, *, timeout: datetime.timedelta = None, break_old_locks: bool = True) -> bool:
        """
        Acquire a lock.

        :param timeout: the time frame to acquire the lock.
            If none is set, this function will use the default_blocking_timeout.
        :param break_old_locks: set to False to ignore old locks. Default True.
        :return: True on success; otherwise throws a LockedException.
        """
        if timeout is None:
            timeout = self.default_blocking_timeout
        try_lock_start_time = time.time()
        while time.time() - try_lock_start_time < timeout.total_seconds():
            if self._acquire_lock(break_old_locks=break_old_locks):
                return True
            else:
                doze(CACHE_UNLOCK_WAIT_TIME)
        raise LockedException("Could not obtain a lock on the file cache within timeout: {timeout}."
                              " Please try again later.".format(**{'timeout': str(timeout)}))

    def release(self) -> None:
        """Release lock or do nothing if lock is not held"""
        if self.held:
            try:
                shutil.rmtree(self.lock_dir_path)
                self.held = False
            except OSError as err:
                if err.errno != errno.ENOENT:
                    raise

    def _get_age(self) -> int:
        """Return the age of the lock"""
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
        """
        if self.held:
            return True
        try:
            os.makedirs(self.lock_dir_path)
            self.held = True
            # Make sure the modification times are correct
            # On some machines, the modification time could be seconds off
            os.utime(self.lock_dir_path, (0, time.time()))
        except OSError as err:
            if err.errno != errno.EEXIST and err.errno != errno.EACCES:
                raise
            # already locked...
            if break_old_locks and self._get_age() > self.max_age.total_seconds():
                self.held = True
                # Make sure the modification times are correct
                # On some machines, the modification time could be seconds off
                os.utime(self.lock_dir_path, (0, time.time()))
            else:
                self.held = False
        return self.held

    # Make the lock object a Context Manager
    def __enter__(self) -> None:
        self.blocking_acquire()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()
