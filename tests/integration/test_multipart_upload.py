import pytest

from spccore.multipart_upload import *
from spccore.multipart_upload import _multipart_upload_status, _get_batch_pre_signed_url, _upload_part, _add_part, \
_complete_multipart_upload


@pytest.fixture
def file_name():
    file_name = "test_upload_single_chunk.txt"
    with open(file_name, 'wb') as writer:
        writer.write(os.urandom(200))
    yield file_name
    os.remove(file_name)


def test_upload_single_chunk(test_user_client, file_name):

    md5 = get_md5_hex_digest(file_name)
    content_type = "text/plain"

    # start upload
    status = _multipart_upload_status(test_user_client,
                                      file_name,
                                      content_type=content_type,
                                      file_size_byte=os.path.getsize(file_name),
                                      md5_hex_digest=md5)

    assert status is not None
    assert status['state'] == UPLOADING_STATE
    upload_id = int(status['uploadId'])

    # get pre-signed url for chunk 1
    batch_presigned_urls = list(_get_batch_pre_signed_url(test_user_client, upload_id, content_type, [1]))

    assert len(batch_presigned_urls) == 1

    # upload the entire file as 1 chunk
    with open(file_name, 'rb') as reader:
        part = reader.read()
        _upload_part(batch_presigned_urls[0]['uploadPresignedUrl'], part)

    # add that chunk
    add_part_response = _add_part(test_user_client, upload_id, 1, md5)
    assert add_part_response is not None
    assert add_part_response['addPartState'] == ADD_PART_STATE_SUCCESS

    # complete upload
    status = _complete_multipart_upload(test_user_client, upload_id)
    assert status is not None
    assert status['state'] == COMPLETE_STATE
