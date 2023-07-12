import hashlib

from spccore.constants import KB, MB

DEFAULT_BUFFER_SIZE_BYTE = 8 * KB
DEFAULT_BLOCK_SIZE_BYTE = 2 * MB


def get_md5_hex_digest_for_file(file_path: str, *, block_size_byte: int = DEFAULT_BLOCK_SIZE_BYTE) -> str:
    """
    Calculate and return the MD5 of the given file.
    See `source <http://stackoverflow.com/questions/1131220/get-md5-hash-of-a-files-without-open-it-in-python>`_.

    :param file_path: The target file to calculate
    :param block_size_byte: The number of bytes to read in at once. Defaults to 2 MB.
    :returns: The hex digest of the MD5 for the given file
    :raises FileNotFoundError: when the given file_path does not exist
    """

    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(block_size_byte)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def get_md5_hex_digest_for_bytes(data: bytes) -> str:
    """
    Calculates and return the MD5 for a given buffer

    :param data: the data in bytes
    :return: the hex digest of the MD5
    """
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def get_part_data(file_path: str, part_number: int, part_size: int) -> bytes:
    """
    Return the bytes for a given part_number of a file

    :param file_path: the given file
    :param part_number: the index of the part in the given buffer. The first part's index is 1.
    :param part_size: the max size of each part
    :return: the bytes of the target part
    :raises FileNotFoundError: when the given file_path does not exist
    """
    with open(file_path, 'rb') as f:
        f.seek((part_number-1)*part_size)
        return f.read(part_size)
