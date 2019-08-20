import pytest
from unittest.mock import Mock, patch

from spccore.baseclient import SynapseBaseClient
from spccore.multipart_upload import *
from spccore.multipart_upload import _multipart_upload_status, _get_batch_pre_signed_url, _upload_part, _add_part,\
    _complete_multipart_upload


@pytest.fixture
def client():
    client = Mock(SynapseBaseClient)
    client.default_file_endpoint = SYNAPSE_DEFAULT_FILE_ENDPOINT
    return client


@pytest.fixture
def file_name():
    return "test.txt"


@pytest.fixture
def small_file_size():
    return 200


@pytest.fixture
def content_type():
    return "text/plain"


@pytest.fixture
def md5():
    return "a6022ff801a82913d23cdf614b47a69f"


@pytest.fixture
def upload_id():
    return 3241


@pytest.fixture
def presigned_url():
    return "http://domain.com/upload/3241"


@pytest.fixture
def data():
    return r'some raw data'


@pytest.fixture
def status():
    return {
        "uploadId": "13622523",
        "startedBy": "3385922",
        "updatedOn": "2019-02-21T21:04:57.000Z",
        "state": "UPLOADING",
        "partsState": "0",
        "startedOn": "2019-02-21T21:04:57.000Z"
    }


@pytest.fixture
def status_request_body(file_name, content_type, small_file_size, md5):
    return {
        'contentMD5Hex': md5,
        'contentType': content_type,
        'fileSizeBytes': small_file_size,
        'partSizeBytes': SYNAPSE_DEFAULT_UPLOAD_PART_SIZE,
        'fileName': file_name,
        'storageLocationId': SYNAPSE_DEFAULT_STORAGE_LOCATION_ID,
        'generatePreview': True
    }


# _multipart_upload_status
def test_multipart_upload_status_invalid_file_name(client, content_type, small_file_size, md5):
    invalid_file_name = 1
    with patch.object(client, "post") as mock_post, \
            pytest.raises(TypeError):
        _multipart_upload_status(client, invalid_file_name, content_type, small_file_size, md5)
        mock_post.assert_not_called()


def test_multipart_upload_status_invalid_content_type(client, file_name, small_file_size, md5):
    invalid_content_type = 1
    with patch.object(client, "post") as mock_post, \
            pytest.raises(TypeError):
        _multipart_upload_status(client, file_name, invalid_content_type, small_file_size, md5)
        mock_post.assert_not_called()


def test_multipart_upload_status_invalid_file_size(client, file_name, content_type, md5):
    invalid_file_size = "invalid"
    with patch.object(client, "post") as mock_post, \
            pytest.raises(TypeError):
        _multipart_upload_status(client, file_name, content_type, small_file_size, invalid_file_size, md5)
        mock_post.assert_not_called()


def test_multipart_upload_status_invalid_md5(client, file_name, content_type, small_file_size):
    invalid_md5 = 1
    with patch.object(client, "post") as mock_post, \
            pytest.raises(TypeError):
        _multipart_upload_status(client, file_name, content_type, small_file_size, invalid_md5)
        mock_post.assert_not_called()


def test_multipart_upload_status(client, file_name, content_type, small_file_size, md5, status_request_body, status):
    with patch.object(client, "post", return_value=status) as mock_post:
        assert status == _multipart_upload_status(client, file_name, content_type, small_file_size, md5)
        mock_post.assert_called_once_with(SYNAPSE_URL_PATH_MULTIPART_UPLOAD_STATUS,
                                          endpoint=SYNAPSE_DEFAULT_FILE_ENDPOINT,
                                          request_body=status_request_body)


def test_multipart_upload_status_force_restart(client,
                                               file_name,
                                               content_type,
                                               small_file_size,
                                               md5,
                                               status_request_body,
                                               status):
    with patch.object(client, "post", return_value=status) as mock_post:
        assert status == _multipart_upload_status(client,
                                                  file_name,
                                                  content_type,
                                                  small_file_size,
                                                  md5,
                                                  force_restart=True)
        mock_post.assert_called_once_with(SYNAPSE_URL_PATH_MULTIPART_UPLOAD_STATUS + '?forceRestart=True',
                                          endpoint=SYNAPSE_DEFAULT_FILE_ENDPOINT,
                                          request_body=status_request_body)


# _get_batch_pre_signed_url

# _upload_part

# _add_part

# _complete_multipart_upload