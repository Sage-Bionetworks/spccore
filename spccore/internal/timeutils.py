import datetime
import platform

"""
Epoch time is in millisecond precision. In Python time.time() and datetime.datetime.utcfromtimestamp() operates on float
with millisecond precision. For example 123.456 represents 123456 milliseconds.

The methods above takes and returns float in millisecond precision even though the unit before the decimal point is in
second.

Example::

    from_epoch_time_to_iso(1561939380.9995)                              #'2019-07-01T00:03:01.000Z'

    from_datetime_to_iso(datetime.datetime(2019, 7, 1, 0, 3, 0, 999500)) #'2019-07-01T00:03:01.000Z'

    from_epoch_time_to_datetime(1561939380.9995)                         #datetime.datetime(2019, 7, 1, 0, 3, 0, 999500)

    from_datetime_to_epoch_time(datetime.datetime(2019, 7, 1, 0, 3, 0, 999500)) #1561939380.9995
"""

UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)


def from_epoch_time_to_iso(epoch_time: float) -> str:
    """
    Convert epoch time in millisecond precision since midnight Jan 1, 1970 to a string in ISO format.
    """
    return None if epoch_time is None else from_datetime_to_iso(from_epoch_time_to_datetime(epoch_time))


def from_datetime_to_iso(dt: datetime.datetime) -> str:
    """
    Round microseconds to milliseconds and add back the "Z" (timezone) at the end.

    :param dt: the datetime object that represents a time
    :return: a string representation of the datetime of object
    """
    fmt = "{time.year:04}-{time.month:02}-{time.day:02}" \
          "{sep}{time.hour:02}:{time.minute:02}:{time.second:02}.{millisecond:03}{tz}"
    # rounding without accounting for this case would lead to '00.1000Z' instead of '01.000Z'
    if dt.microsecond >= 999500:
        dt -= datetime.timedelta(microseconds=dt.microsecond)
        dt += datetime.timedelta(seconds=1)
    return fmt.format(time=dt, millisecond=int(round(dt.microsecond / 1000.0)), tz="Z", sep="T")


def from_epoch_time_to_datetime(epoch_time: float) -> datetime.datetime:
    """
    Returns a datetime object representation of a given time in milliseconds since midnight Jan 1, 1970.

    :param epoch_time: time in millisecond precision since midnight Jan 1, 1970
    """

    # utcfromtimestamp() fails for negative values (dates before 1970-1-1) on Windows
    # so, here's a hack that enables ancient events, such as Chris's birthday, to be
    # converted from milliseconds since the UNIX epoch to higher level Datetime objects. Ha!
    if platform.system() == 'Windows' and epoch_time < 0:
        mirror_date = datetime.datetime.utcfromtimestamp(abs(epoch_time))
        return UNIX_EPOCH - (mirror_date - UNIX_EPOCH)
    return datetime.datetime.utcfromtimestamp(epoch_time)


def from_datetime_to_epoch_time(dt: datetime) -> float:
    """
    Convert either datetime.datetime objects to epoch time in millisecond precision.
    """
    return (dt - UNIX_EPOCH).total_seconds()
