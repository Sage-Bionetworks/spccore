from spccore.internal.timeutils import *


def test_from_epoch_time_to_iso():
    assert from_epoch_time_to_iso(None) is None
    assert from_epoch_time_to_iso(0) == '1970-01-01T00:00:00.000Z'
    assert from_epoch_time_to_iso(1561939380.9995) == '2019-07-01T00:03:01.000Z'
    assert from_epoch_time_to_iso(-6106060800.0) == '1776-07-04T00:00:00.000Z'


def test_from_datetime_to_iso():
    assert from_datetime_to_iso(UNIX_EPOCH) == '1970-01-01T00:00:00.000Z'
    assert from_datetime_to_iso(datetime.datetime(2019, 7, 1, 0, 3, 0, 999499)) == '2019-07-01T00:03:00.999Z'
    assert from_datetime_to_iso(datetime.datetime(2019, 7, 1, 0, 3, 0, 999500)) == '2019-07-01T00:03:01.000Z'
    assert from_datetime_to_iso(datetime.datetime(1776, 7, 4, 0, 0, 0)) == '1776-07-04T00:00:00.000Z'


def test_from_epoch_time_to_datetime():
    assert from_epoch_time_to_datetime(0) == UNIX_EPOCH
    assert from_epoch_time_to_datetime(1561939380.9995) == datetime.datetime(2019, 7, 1, 0, 3, 0, 999500)
    assert from_epoch_time_to_datetime(-6106060800.0) == datetime.datetime(1776, 7, 4, 0, 0, 0)


def test_from_datetime_to_epoch_time():
    assert from_datetime_to_epoch_time(datetime.datetime(1776, 7, 4, 0, 0, 0)) == -6106060800.0
    assert from_datetime_to_epoch_time(datetime.datetime(2019, 7, 1, 0, 3, 0, 999500)) == 1561939380.9995
    assert from_datetime_to_epoch_time(UNIX_EPOCH) == 0
