import threading
from spccore.internal.dozer import *


def teardown_function():
    clear_listeners()


def test_doze():
    class CounterClass(object):
        def __init__(self):
            self.val = 0

        def __call__(self):
            self.val = self.val + 1

    counter = CounterClass()

    # register Listener
    add_listener(counter)
    doze(1)  # should call counter to increase values about 10 times
    assert counter.val == 10


def test_add_listener_with_multiple_threads():
    threads = [threading.Thread(target=add_listener, args=(lambda _: print(1),)),
               threading.Thread(target=add_listener, args=(lambda _: print(2),))]

    import spccore.internal.dozer
    assert len(spccore.internal.dozer._listeners) == 0

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(spccore.internal.dozer._listeners) == 2


def test_dozer_with_multiple_threads():
    def f1():
        import spccore.internal.dozer
        spccore.internal.dozer._listeners = [lambda _: print(1)]

    def f2():
        from spccore.internal.dozer import add_listener
        add_listener(lambda _: print(2))

    threads = [threading.Thread(target=f1), threading.Thread(target=f2)]

    import spccore.internal.dozer
    assert len(spccore.internal.dozer._listeners) == 0

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert len(spccore.internal.dozer._listeners) == 2
