"""
Created on Sep 21, 2017

@author: bhoff

sleep while checking registered _listeners
"""
import time
import typing

_listeners = []


def add_listener(listener: typing.Callable) -> None:
    """Register a new callable listener"""

    if not callable(listener):
        raise ValueError("listener is not callable")
    _listeners.append(listener)


def clear_listeners() -> None:
    """Remove all listeners"""

    del _listeners[:]


def doze(wait_secs: float, listener_check_interval_secs=0.1) -> None:
    """Wait for a given wait_secs before executing the callable listeners"""

    exec_time = time.time() + wait_secs
    while time.time() < exec_time:
        for listener in _listeners:
            listener()
        time.sleep(listener_check_interval_secs)
