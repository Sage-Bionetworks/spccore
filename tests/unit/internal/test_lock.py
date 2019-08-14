import pytest
from unittest.mock import patch, call

from spccore.internal.lock import *


@pytest.fixture
def lock(name, cwd, max_age, timeout):
    return Lock(name, current_working_directory=cwd, max_age=max_age, default_blocking_timeout=timeout)


@pytest.fixture
def name():
    return "some_folder"


@pytest.fixture
def cwd():
    return "test_dir"


@pytest.fixture
def max_age():
    return datetime.timedelta(seconds=1)


@pytest.fixture
def timeout():
    return datetime.timedelta(seconds=5)


@pytest.fixture
def lock_dir_path(cwd, name):
    return cwd+"/"+name+"."+LOCK_FILE_SUFFIX


@pytest.fixture
def error():
    error = OSError()
    error.errno = errno.EACCES
    return error


class TestLock:

    # __init__
    def test_constructor(self, name, cwd, lock_dir_path):
        with patch.object(os, "getcwd", return_value=cwd) as mock_getcwd, \
                patch.object(os.path, "join", return_value=lock_dir_path) as mock_join:
            lock = Lock(name)
            assert lock.name == name
            assert lock.last_updated_time is None
            assert lock.current_working_directory == cwd
            assert lock.lock_dir_path == lock_dir_path
            assert lock.max_age == LOCK_DEFAULT_MAX_AGE
            assert lock.default_blocking_timeout == DEFAULT_BLOCKING_TIMEOUT
            mock_getcwd.assert_called_once_with()
            mock_join.assert_called_once_with(cwd, name+"."+LOCK_FILE_SUFFIX)

    def test_custom_lock(self, name, cwd, lock_dir_path, max_age, timeout):
        with patch.object(os, "getcwd") as mock_getcwd, \
                patch.object(os.path, "join", return_value=lock_dir_path) as mock_join:
            lock = Lock(name, current_working_directory=cwd, max_age=max_age, default_blocking_timeout=timeout)
            assert lock.name == name
            assert lock.current_working_directory == cwd
            assert lock.lock_dir_path == lock_dir_path
            assert lock.max_age == max_age
            assert lock.default_blocking_timeout == timeout
            mock_getcwd.assert_not_called()
            mock_join.assert_called_once_with(cwd, name + "." + LOCK_FILE_SUFFIX)

    # _has_lock
    def test_private_has_lock(self, lock):
        lock.last_updated_time = from_epoch_time_to_iso(0)
        with patch.object(os.path, "getmtime", return_value=0) as mock_get_mtime:
            assert lock._has_lock()
            mock_get_mtime.assert_called_once_with(lock.lock_dir_path)

    def test_private_has_lock_out_of_date(self, lock):
        lock.last_updated_time = from_epoch_time_to_iso(0)
        with patch.object(os.path, "getmtime", return_value=1) as mock_get_mtime:
            assert lock._has_lock() is False
            mock_get_mtime.assert_called_once_with(lock.lock_dir_path)

    def test_private_has_lock_fails(self, lock, error):
        lock.last_updated_time = from_epoch_time_to_iso(0)
        with patch.object(os.path, "getmtime", side_effect=error) as mock_get_mtime:
            assert lock._has_lock() is False
            mock_get_mtime.assert_called_once_with(lock.lock_dir_path)

    # _get_age
    def test_private_get_age(self, lock):
        with patch.object(time, "time", return_value=2) as mock_time, \
                patch.object(os.path, "getmtime", return_value=1) as mock_getmtime:
            assert 1 == lock._get_age()
            mock_time.assert_called_once_with()
            mock_getmtime.assert_called_once_with(lock.lock_dir_path)

    def test_private_get_age_throws_error(self, lock):
        with pytest.raises(OSError), \
                patch.object(time, "time", return_value=2) as mock_time, \
                patch.object(os.path, "getmtime", side_effect=OSError()) as mock_getmtime:
            lock._get_age()
            mock_time.assert_called_once_with()
            mock_getmtime.assert_called_once_with(lock.lock_dir_path)

    def test_private_get_age_throws_known_error(self, lock, error):
        with patch.object(time, "time", return_value=2) as mock_time, \
                patch.object(os.path, "getmtime", side_effect=error) as mock_getmtime:
            assert 0 == lock._get_age()
            mock_time.assert_called_once_with()
            mock_getmtime.assert_called_once_with(lock.lock_dir_path)

    # _acquire_lock
    def test_private_acquire_lock_with_renew(self, lock):
        with patch.object(lock, "renew", return_value=True) as mock_renew, \
                patch.object(os, "makedirs") as mock_makedirs, \
                patch.object(os, "utime") as mock_utime, \
                patch.object(time, "time") as mock_time, \
                patch.object(lock, "_get_age", return_value=lock.max_age.total_seconds()+1) as mock_get_age, \
                patch.object(lock, "_has_lock", return_value=True) as mock_has_lock:
            assert lock._acquire_lock()
            mock_renew.assert_called_once_with()
            mock_makedirs.assert_not_called()
            mock_utime.assert_not_called()
            mock_time.assert_not_called()
            mock_get_age.assert_not_called()
            mock_has_lock.assert_not_called()

    def test_private_acquire_lock_with_uncaught_error(self, lock):
        utime = 1
        with pytest.raises(OSError), \
                patch.object(lock, "renew", return_value=False) as mock_renew, \
                patch.object(os, "makedirs") as mock_makedirs, \
                patch.object(os, "utime", side_effect=OSError()) as mock_utime, \
                patch.object(time, "time", return_value=utime) as mock_time, \
                patch.object(lock, "_get_age", return_value=lock.max_age.total_seconds()+1) as mock_get_age, \
                patch.object(lock, "_has_lock", return_value=True) as mock_has_lock:
            lock._acquire_lock()
            mock_renew.assert_not_called()
            mock_makedirs.assert_called_once_with(lock.lock_dir_path)
            mock_utime.assert_called_once_with(lock.lock_dir_path, (0, utime))
            mock_time.assert_called_once_with()
            mock_get_age.assert_not_called()
            mock_has_lock.assert_not_called()

    def test_private_acquire_lock_not_break_old_lock(self, lock, error):
        utime = 1
        with patch.object(lock, "renew", return_value=False) as mock_renew, \
                patch.object(os, "makedirs") as mock_makedirs, \
                patch.object(os, "utime", side_effect=error) as mock_utime, \
                patch.object(time, "time", return_value=utime) as mock_time, \
                patch.object(lock, "_get_age", return_value=lock.max_age.total_seconds()+1) as mock_get_age, \
                patch.object(lock, "_has_lock", return_value=True) as mock_has_lock:
            assert lock._acquire_lock(break_old_locks=False) is False
            mock_renew.assert_called_once_with()
            mock_makedirs.assert_called_once_with(lock.lock_dir_path)
            mock_utime.assert_called_once_with(lock.lock_dir_path, (0, utime))
            mock_time.assert_called_once_with()
            mock_get_age.assert_not_called()
            mock_has_lock.assert_not_called()

    def test_private_acquire_lock_break_old_lock(self, lock, error):
        utime = 1
        with patch.object(lock, "renew", return_value=False) as mock_renew, \
                patch.object(os, "makedirs", side_effect=error) as mock_makedirs, \
                patch.object(os, "utime") as mock_utime, \
                patch.object(time, "time", return_value=utime) as mock_time, \
                patch.object(lock, "_get_age", return_value=lock.max_age.total_seconds()+1) as mock_get_age, \
                patch.object(lock, "_has_lock", return_value=True) as mock_has_lock:
            assert lock._acquire_lock()
            mock_renew.assert_called_once_with()
            mock_makedirs.assert_called_once_with(lock.lock_dir_path)
            mock_utime.assert_called_once_with(lock.lock_dir_path, (0, utime))
            mock_time.assert_called_once_with()
            mock_get_age.assert_called_once_with()
            mock_has_lock.assert_called_once_with()

    def test_private_acquire_lock_break_old_lock_with_non_expired_lock(self, lock, error):
        utime = 1
        with patch.object(lock, "renew", return_value=False) as mock_renew, \
                patch.object(os, "makedirs", side_effect=error) as mock_makedirs, \
                patch.object(os, "utime") as mock_utime, \
                patch.object(time, "time", return_value=utime) as mock_time, \
                patch.object(lock, "_get_age", return_value=lock.max_age.total_seconds()-1) as mock_get_age, \
                patch.object(lock, "_has_lock", return_value=True) as mock_has_lock:
            assert lock._acquire_lock() is False
            mock_renew.assert_called_once_with()
            mock_makedirs.assert_called_once_with(lock.lock_dir_path)
            mock_utime.assert_not_called()
            mock_time.assert_not_called()
            mock_get_age.assert_called_once_with()
            mock_has_lock.assert_not_called()

    # __enter__
    def test_private_enter(self, lock):
        with patch.object(lock, "blocking_acquire") as mock_blocking_acquire:
            assert lock == lock.__enter__()
            mock_blocking_acquire.assert_called_once_with()

    # __exit__
    def test_private_exit(self, lock):
        with patch.object(lock, "release") as mock_release:
            lock.__exit__(None, None, None)
            mock_release.assert_called_once_with()

    # renew
    def test_renew_not_already_have_lock(self, lock):
        with patch.object(lock, "_has_lock", return_value=False) as mock_has_lock, \
                patch.object(lock, "_get_age", return_value=0) as mock_get_age, \
                patch.object(os, "utime") as mock_utime, \
                patch.object(time, "time") as mock_time:
            assert lock.renew() is False
            mock_has_lock.assert_called_once_with()
            mock_utime.assert_not_called()
            mock_time.assert_not_called()
            mock_get_age.assert_not_called()

    def test_renew_lock_fails(self, lock):
        utime = 1
        with patch.object(lock, "_has_lock", return_value=True) as mock_has_lock, \
                patch.object(os, "utime", side_effect=OSError()) as mock_utime, \
                patch.object(lock, "_get_age", return_value=0) as mock_get_age, \
                patch.object(time, "time", return_value=utime) as mock_time:
            assert lock.renew() is False
            mock_has_lock.assert_called_once_with()
            mock_utime.assert_called_once_with(lock.lock_dir_path, (0, utime))
            mock_time.assert_called_once_with()
            mock_get_age.assert_called_once_with()

    def test_renew_lock_success(self, lock):
        utime = 1
        with patch.object(lock, "_has_lock", return_value=True) as mock_has_lock, \
                patch.object(os, "utime") as mock_utime, \
                patch.object(lock, "_get_age", return_value=0) as mock_get_age, \
                patch.object(time, "time", return_value=utime) as mock_time:
            assert lock.renew()
            mock_has_lock.assert_called_once_with()
            mock_utime.assert_called_once_with(lock.lock_dir_path, (0, utime))
            mock_time.assert_called_once_with()
            mock_get_age.assert_called_once_with()

    # release
    def test_release_not_have_lock(self, lock):
        with patch.object(lock, "_has_lock", return_value=False) as mock_has_lock, \
                patch.object(shutil, "rmtree") as mock_rmtree:
            lock.release()
            mock_rmtree.assert_not_called()
            mock_has_lock.assert_called_once_with()

    def test_release_success(self, lock):
        with patch.object(lock, "_has_lock", return_value=True) as mock_has_lock, \
                patch.object(shutil, "rmtree") as mock_rmtree:
            lock.release()
            mock_rmtree.assert_called_once_with(lock.lock_dir_path)
            mock_has_lock.assert_called_once_with()

    def test_release_throws_error(self, lock):
        with patch.object(lock, "_has_lock", return_value=True) as mock_has_lock, \
                pytest.raises(OSError), \
                patch.object(shutil, "rmtree", side_effect=OSError()) as mock_rmtree:
            lock.release()
            mock_rmtree.assert_called_once_with(lock.lock_dir_path)
            mock_has_lock.assert_called_once_with()

    # blocking_acquire
    def test_blocking_acquire(self, lock):
        with patch.object(time, "time", side_effect=(0, 1, 2)) as mock_time, \
                patch.object(lock, "_acquire_lock", side_effect=(False, True)) as mock_acquire_lock, \
                patch("spccore.internal.lock.doze") as mock_doze:
            assert lock.blocking_acquire()
            assert mock_time.call_count == 3
            mock_acquire_lock.assert_has_calls([call(break_old_locks=True), call(break_old_locks=True)])
            mock_doze.assert_called_once_with(CACHE_UNLOCK_WAIT_TIME_SEC)

    def test_blocking_acquire_timeout(self, lock):
        with pytest.raises(LockException), \
                patch.object(time, "time", side_effect=(0, 1, 2)) as mock_time, \
                patch.object(lock, "_acquire_lock", side_effect=(False, True)) as mock_acquire_lock, \
                patch("spccore.internal.lock.doze") as mock_doze:
            lock.blocking_acquire(timeout=datetime.timedelta(seconds=2))
            assert mock_time.call_count == 3
            mock_acquire_lock.assert_has_calls([call(break_old_locks=True), call(break_old_locks=True)])
            mock_doze.assert_called_once_with(CACHE_UNLOCK_WAIT_TIME_SEC)

    def test_blocking_acquire_with_no_break_old_lock(self, lock):
        with patch.object(time, "time", side_effect=(0, 1)) as mock_time, \
                patch.object(lock, "_acquire_lock", return_value=True) as mock_acquire_lock, \
                patch("spccore.internal.lock.doze") as mock_doze:
            assert lock.blocking_acquire(break_old_locks=False)
            assert mock_time.call_count == 2
            mock_acquire_lock.assert_has_calls([call(break_old_locks=False)])
            mock_doze.assert_not_called()
