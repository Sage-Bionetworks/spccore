from spccore.internal.fileutils import *


def test_get_md5_hex_digest(tiny_file):
    file_name, data = tiny_file
    md5 = hashlib.md5()
    md5.update(data)
    assert md5.hexdigest() == get_md5_hex_digest(file_name, block_size_byte=10)
