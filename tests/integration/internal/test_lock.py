from spccore.internal.lock import *


def test_private_acquire():
    user1_lock = Lock("foo", max_age=datetime.timedelta(seconds=2))
    user2_lock = Lock("foo", max_age=datetime.timedelta(seconds=2))
    assert user1_lock._has_lock() is False
    assert user2_lock._has_lock() is False

    assert user1_lock._acquire_lock()
    assert user1_lock._get_age() < 2
    assert user2_lock._acquire_lock() is False

    user1_lock.release()

    assert user2_lock._acquire_lock()
    assert user1_lock._acquire_lock() is False

    user2_lock.release()


def test_context_manager():
    user1_lock = Lock("foo", max_age=datetime.timedelta(seconds=2))
    user2_lock = Lock("foo", max_age=datetime.timedelta(seconds=2))

    with user1_lock:
        assert user1_lock._has_lock()
        assert user1_lock._get_age() < 2
        assert user2_lock._acquire_lock() is False

    assert user1_lock._has_lock() is False
    assert user2_lock._has_lock() is False


def test_lock_timeout():
    user1_lock = Lock("foo", max_age=datetime.timedelta(seconds=1))
    user2_lock = Lock("foo", max_age=datetime.timedelta(seconds=1))

    with user1_lock:
        assert user1_lock._has_lock()
        assert user1_lock._get_age() < 1.0
        assert user2_lock._acquire_lock(break_old_locks=True) is False
        time.sleep(2)
        assert user1_lock._get_age() > 1.0
        assert user2_lock._acquire_lock(break_old_locks=True)

    assert user2_lock._has_lock()
    user2_lock.release()


def test_renew():
    user_lock = Lock(".foo", max_age=datetime.timedelta(seconds=2))
    with user_lock:
        time.sleep(1.1)
        assert user_lock._get_age() > 1.0
        assert user_lock.renew()
        assert user_lock._get_age() < 1.0


def test_renew_with_expired():
    user_lock = Lock("foo", max_age=datetime.timedelta(seconds=1))
    with user_lock:
        time.sleep(1.1)
        assert user_lock._get_age() > 1.0
        # expired but has not released
        assert user_lock.renew() is False


def test_release():
    user1_lock = Lock("foo", max_age=datetime.timedelta(seconds=2))
    user2_lock = Lock("foo", max_age=datetime.timedelta(seconds=2))
    assert user1_lock._acquire_lock()
    user1_lock.release()
    assert user1_lock._has_lock() is False
    assert user2_lock._acquire_lock()
    assert user1_lock._acquire_lock() is False

    user2_lock.release()


def test_nested_context_managers():
    with Lock(".foo", max_age=datetime.timedelta(seconds=2)) as user1_lock:
        with Lock(".foo", max_age=datetime.timedelta(seconds=2)) as user2_lock:
            assert user2_lock._has_lock()
        assert user1_lock._has_lock() is False
