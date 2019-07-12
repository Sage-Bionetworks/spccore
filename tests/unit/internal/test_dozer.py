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
