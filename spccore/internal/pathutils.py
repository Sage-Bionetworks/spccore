import math
import os
import re
import typing

from spccore.internal.timeutils import *


# To be compatible with R
def normalize_path(path: str) -> typing.Union[str, None]:
    """Transforms a path into an absolute path with forward slashes only."""
    if path is None:
        return None
    return re.sub(r'\\', '/', os.path.normcase(os.path.abspath(path)))


def get_modified_time_in_iso(path: str) -> typing.Union[str, None]:
    """Return the last modified time of a file / folder identified by path in iso format"""
    if os.path.exists(path):
        return from_epoch_time_to_iso(math.floor(os.path.getmtime(path)))
    return None


def get_modified_time(path: str) -> typing.Union[int, None]:
    """Return the last modified time of a file / folder identified by path"""
    if os.path.exists(path):
        return os.path.getmtime(path)
    return None
