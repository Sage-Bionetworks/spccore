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
def pre_signed_url():
    return "http://domain.com/upload/3241"


@pytest.fixture
def data():
    return rb'some raw data'


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


@pytest.fixture
def pre_signed_url_batch_response(pre_signed_url):
    return {
        'partPresignedUrls': [
            {'partNumber': 1,
             'uploadPresignedUrl': pre_signed_url}
        ]
    }


@pytest.fixture
def parts():
    return [1]


@pytest.fixture
def pre_signed_url_request(upload_id, parts):
    return {
        'uploadId': upload_id,
        'partNumbers': parts
    }


@pytest.fixture
def upload_part_response():
    response = Mock(requests.Response)
    response.content = "some response text"
    return response


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
                                          request_body=status_request_body,
                                          endpoint=SYNAPSE_DEFAULT_FILE_ENDPOINT)


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
                                          request_body=status_request_body,
                                          endpoint=SYNAPSE_DEFAULT_FILE_ENDPOINT)


# _get_batch_pre_signed_url
def test_get_batch_pre_signed_url_invalid_upload_id(client, content_type):
    with patch.object(client, "post") as mock_post, \
            pytest.raises(TypeError):
        assert [] == list(_get_batch_pre_signed_url(client, "invalid_upload_id", content_type, []))
        mock_post.assert_not_called()


def test_get_batch_pre_signed_url_invalid_content_type(client, upload_id):
    invalid_content_type = 1
    with patch.object(client, "post") as mock_post, \
            pytest.raises(TypeError):
        assert [] == list(_get_batch_pre_signed_url(client, upload_id, invalid_content_type, []))
        mock_post.assert_not_called()


def test_get_batch_pre_signed_url_empty_batch(client, upload_id, content_type):
    with patch.object(client, "post") as mock_post:
        assert [] == list(_get_batch_pre_signed_url(client, upload_id, content_type, []))
        mock_post.assert_not_called()


def test_get_batch_pre_signed_url(client,
                                  upload_id,
                                  content_type,
                                  parts,
                                  pre_signed_url_request,
                                  pre_signed_url_batch_response):
    with patch.object(client, "post", return_value=pre_signed_url_batch_response) as mock_post:
        batch = list(_get_batch_pre_signed_url(client, upload_id, content_type, parts))
        assert pre_signed_url_batch_response['partPresignedUrls'] == batch
        mock_post.assert_called_once_with(
            SYNAPSE_URL_PATH_MULTIPART_UPLOAD_GET_BATCH_PRESIGNED_URL.format(upload_id=upload_id),
            request_body=pre_signed_url_request,
            endpoint=SYNAPSE_DEFAULT_FILE_ENDPOINT)


# _upload_part
def test_upload_part_invalid_pre_signed_url(data, upload_part_response):
    invalid_pre_signed_url = 1
    with patch.object(requests, "put", return_value=upload_part_response) as mock_put, \
            pytest.raises(TypeError):
        _upload_part(invalid_pre_signed_url, data)
        mock_put.assert_never_called()


def test_upload_part_invalid_data(pre_signed_url, upload_part_response):
    invalid_data = "invalid data"
    with patch.object(requests, "put", return_value=upload_part_response) as mock_put, \
            pytest.raises(TypeError):
        _upload_part(pre_signed_url, invalid_data)
        mock_put.assert_never_called()


def test_upload_part(pre_signed_url, data, upload_part_response):
    with patch.object(requests, "put", return_value=upload_part_response) as mock_put:
        _upload_part(pre_signed_url, data)
        mock_put.assert_called_once_with(pre_signed_url, data=data)


# _add_part


# _complete_multipart_upload
