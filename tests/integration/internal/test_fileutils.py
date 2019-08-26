import os

from spccore.internal.fileutils import *


def test_get_md5_hex_digest(tiny_file):
    file_name, data = tiny_file
    md5 = hashlib.md5()
    md5.update(data)
    assert md5.hexdigest() == get_md5_hex_digest_for_file(file_name, block_size_byte=10)


def test_get_md5_for_bytes_and_get_part_data(tiny_file):
    file_name, data = tiny_file
    md5 = hashlib.md5()
    md5.update(data)
    assert md5.hexdigest() == get_md5_hex_digest_for_bytes(data)
    assert md5.hexdigest() == get_md5_hex_digest_for_bytes(get_part_data(file_name, 1, os.path.getsize(file_name)))