import datetime
import platform

UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)


def from_epoch_time_to_iso(epoch_time: float) -> str:
    """
    Convert seconds since unix epoch to a string in ISO format
    """
    return None if epoch_time is None else from_datetime_to_iso(from_epoch_time_to_datetime(epoch_time))


def from_datetime_to_iso(dt: datetime.datetime, sep: str = "T") -> str:
    """
    Round microseconds to milliseconds and add back the "Z" (timezone) at the end

    :param dt: the datetime object that represents a time
    :param sep:
    :return: a string representation of the datetime of object
    """
    fmt = "{time.year:04}-{time.month:02}-{time.day:02}" \
          "{sep}{time.hour:02}:{time.minute:02}:{time.second:02}.{millisecond:03}{tz}"
    # rounding without accounting for this case would lead to '00.1000Z' instead of '01.000Z'
    if dt.microsecond >= 999500:
        dt -= datetime.timedelta(microseconds=dt.microsecond)
        dt += datetime.timedelta(seconds=1)
    return fmt.format(time=dt, millisecond=int(round(dt.microsecond / 1000.0)), tz="Z", sep=sep)


def from_epoch_time_to_datetime(time_ms: float) -> datetime.datetime:
    """
    Returns a datetime object representation of a given time in milliseconds since midnight Jan 1, 1970.

    :param time_ms: time in milliseconds since midnight Jan 1, 1970
    """

    # utcfromtimestamp() fails for negative values (dates before 1970-1-1) on Windows
    # so, here's a hack that enables ancient events, such as Chris's birthday, to be
    # converted from milliseconds since the UNIX epoch to higher level Datetime objects. Ha!
    if platform.system() == 'Windows' and time_ms < 0:
        mirror_date = datetime.datetime.utcfromtimestamp(abs(time_ms))
        return UNIX_EPOCH - (mirror_date - UNIX_EPOCH)
    return datetime.datetime.utcfromtimestamp(time_ms)


def from_datetime_to_epoch_time(dt: datetime) -> float:
    """
    Convert either datetime.datetime objects to UNIX time.
    """
    return (dt - UNIX_EPOCH).total_seconds()
