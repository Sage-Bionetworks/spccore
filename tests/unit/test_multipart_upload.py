import pytest
from unittest.mock import Mock, patch, call, ANY

from spccore.baseclient import SynapseBaseClient
from spccore.multipart_upload import *
from spccore.multipart_upload import _multipart_upload_status, _get_batch_pre_signed_url, _upload_part, _add_part,\
    _complete_multipart_upload, _upload_and_add_part, _parts_to_upload


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
def file_handle_id():
    return 123456


@pytest.fixture
def pre_signed_url():
    return "http://domain.com/upload/3241"


@pytest.fixture
def data():
    return rb'some raw data'


@pytest.fixture
def uploading_status(upload_id):
    return {
        "uploadId": upload_id,
        "startedBy": "3385922",
        "updatedOn": "2019-02-21T21:04:57.000Z",
        "state": "UPLOADING",
        "partsState": "0",
        "startedOn": "2019-02-21T21:04:57.000Z"
    }


@pytest.fixture
def completed_status(upload_id, file_handle_id):
    return {
        "uploadId": upload_id,
        "startedBy": "3385922",
        "updatedOn": "2019-02-21T21:04:57.000Z",
        "state": "COMPLETED",
        "partsState": "1",
        "startedOn": "2019-02-21T21:04:57.000Z",
        "resultFileHandleId": file_handle_id
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
def part(pre_signed_url):
    return {'partNumber': 1, 'uploadPresignedUrl': pre_signed_url}


@pytest.fixture
def pre_signed_url_generator(part):
    yield part


@pytest.fixture
def part_number():
    return 1


@pytest.fixture
def parts(part_number):
    return [part_number]


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


@pytest.fixture
def add_part_response(upload_id, part_number):
    return {
        'uploadId': upload_id,
        'partNumber': part_number,
        'addPartState': {SYNAPSE_ADD_PART_STATE_SUCCESS}
    }


@pytest.fixture
def status_first_call(client, file_name, content_type, small_file_size, md5):
    return call(client,
                file_name,
                content_type,
                small_file_size,
                md5,
                storage_location_id=SYNAPSE_DEFAULT_STORAGE_LOCATION_ID,
                generate_preview=False,
                force_restart=False)


@pytest.fixture
def status_call(client, file_name, content_type, small_file_size, md5):
    return call(client,
                file_name,
                content_type,
                small_file_size,
                md5,
                storage_location_id=SYNAPSE_DEFAULT_STORAGE_LOCATION_ID,
                generate_preview=False)


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
        _multipart_upload_status(client, file_name, content_type, invalid_file_size, md5)
        mock_post.assert_not_called()


def test_multipart_upload_status_invalid_md5(client, file_name, content_type, small_file_size):
    invalid_md5 = 1
    with patch.object(client, "post") as mock_post, \
            pytest.raises(TypeError):
        _multipart_upload_status(client, file_name, content_type, small_file_size, invalid_md5)
        mock_post.assert_not_called()


def test_multipart_upload_status(client, file_name, content_type, small_file_size, md5, status_request_body,
                                 uploading_status):
    with patch.object(client, "post", return_value=uploading_status) as mock_post:
        assert uploading_status == _multipart_upload_status(client, file_name, content_type, small_file_size, md5)
        mock_post.assert_called_once_with(SYNAPSE_URL_PATH_MULTIPART_UPLOAD_STATUS,
                                          request_body=status_request_body,
                                          endpoint=SYNAPSE_DEFAULT_FILE_ENDPOINT)


def test_multipart_upload_status_force_restart(client,
                                               file_name,
                                               content_type,
                                               small_file_size,
                                               md5,
                                               status_request_body,
                                               uploading_status):
    with patch.object(client, "post", return_value=uploading_status) as mock_post:
        assert uploading_status == _multipart_upload_status(client,
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
    with patch.object(client, "post") as mock_post:
        with pytest.raises(TypeError):
            list(_get_batch_pre_signed_url(client, "invalid_upload_id", content_type, []))
        mock_post.assert_not_called()


def test_get_batch_pre_signed_url_invalid_content_type(client, upload_id):
    invalid_content_type = 1
    with patch.object(client, "post") as mock_post:
        with pytest.raises(TypeError):
            list(_get_batch_pre_signed_url(client, upload_id, invalid_content_type, []))
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
    with patch.object(requests, "put", return_value=upload_part_response) as mock_put:
        with pytest.raises(TypeError):
            _upload_part(invalid_pre_signed_url, data)
        mock_put.assert_not_called()


def test_upload_part_invalid_data(pre_signed_url, upload_part_response):
    invalid_data = "invalid data"
    with patch.object(requests, "put", return_value=upload_part_response) as mock_put:
        with pytest.raises(TypeError):
            _upload_part(pre_signed_url, invalid_data)
        mock_put.assert_not_called()


def test_upload_part(pre_signed_url, data, upload_part_response):
    with patch.object(requests, "put", return_value=upload_part_response) as mock_put:
        _upload_part(pre_signed_url, data)
        mock_put.assert_called_once_with(pre_signed_url, data=data)


# _add_part
def test_add_part_invalid_upload_id(client, part_number, md5, add_part_response):
    with patch.object(client, "put", return_value=add_part_response) as mock_put:
        with pytest.raises(TypeError):
            _add_part(client, "invalid_upload_id", part_number, md5)
        mock_put.assert_not_called()


def test_add_part_invalid_part_number(client, upload_id, md5, add_part_response):
    with patch.object(client, "put", return_value=add_part_response) as mock_put:
        with pytest.raises(TypeError):
            _add_part(client, upload_id, "invalid_part_number", md5)
        mock_put.assert_not_called()


def test_add_part_invalid_md5(client, upload_id, part_number, add_part_response):
    invalid_md5 = 1
    with patch.object(client, "put", return_value=add_part_response) as mock_put:
        with pytest.raises(TypeError):
            _add_part(client, upload_id, part_number, invalid_md5)
        mock_put.assert_not_called()


def test_add_part(client, upload_id, part_number, md5, add_part_response):
    with patch.object(client, "put", return_value=add_part_response) as mock_put:
        assert add_part_response == _add_part(client, upload_id, part_number, md5)
        mock_put.assert_called_once_with(
            SYNAPSE_URL_PATH_MULTIPART_UPLOAD_ADD_PART.format(upload_id=upload_id, part_number=part_number),
            endpoint=client.default_file_endpoint,
            request_parameters={'partMD5Hex': md5})


# _complete_multipart_upload
def test_complete_multipart_upload_invalid_upload_id(client):
    with patch.object(client, "put") as mock_put:
        with pytest.raises(TypeError):
            _complete_multipart_upload(client, "invalid_upload_id")
        mock_put.assert_not_called()


def test_complete_multipart_upload(client, upload_id, completed_status):
    with patch.object(client, "put", return_value=completed_status) as mock_put:
        assert completed_status == _complete_multipart_upload(client, upload_id)
        mock_put.assert_called_once_with(
            SYNAPSE_URL_PATH_MULTIPART_UPLOAD_COMPLETE.format(upload_id=upload_id),
            endpoint=client.default_file_endpoint)


# _upload_and_add_part
def test_upload_and_add_part(client, upload_id, part_number, pre_signed_url, data, md5, add_part_response):
    with patch("spccore.multipart_upload.get_md5_hex_digest_for_bytes", return_value=md5) as mock_get_md5, \
            patch("spccore.multipart_upload._upload_part") as mock_upload_part, \
            patch("spccore.multipart_upload._add_part", return_value=add_part_response) as mock_add_part:
        assert add_part_response == _upload_and_add_part(client, upload_id, part_number, pre_signed_url, data)
        mock_get_md5.assert_called_once_with(data)
        mock_upload_part.assert_called_once_with(pre_signed_url, data)
        mock_add_part.assert_called_once_with(client, upload_id, part_number, md5)


# _parts_to_upload
def test_parts_to_upload():
    assert [] == _parts_to_upload("")
    assert [] == _parts_to_upload("1")
    assert [] == _parts_to_upload("11")
    assert [1] == _parts_to_upload("0")
    assert [2, 3] == _parts_to_upload("100")


# multipart_upload_file
def test_multipart_upload_file_invalid_file_path(client, file_name, small_file_size, content_type, data, md5,
                                                 part_number, uploading_status, completed_status, pre_signed_url,
                                                 add_part_response, upload_id, file_handle_id, status_first_call,
                                                 status_call, part, pre_signed_url_generator, parts):
    status_list = [uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()
    invalid_file_path = 1

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type") as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete:
        with pytest.raises(TypeError):
            multipart_upload_file(client, invalid_file_path, content_type)
        mock_exist.assert_not_called()
        mock_isdir.assert_not_called()
        mock_basename.assert_not_called()
        mock_getsize.assert_not_called()
        mock_guess_type.assert_not_called()
        mock_get_md5.assert_not_called()
        mock_get_status.assert_not_called()
        mock_get_pool.assert_not_called()
        mock_get_pre_signed_url.assert_not_called()
        mock_complete.assert_not_called()
        mock_map.assert_not_called()


def test_multipart_upload_file_invalid_content_type(client, file_name, small_file_size, content_type, data, md5,
                                                    part_number, uploading_status, completed_status, pre_signed_url,
                                                    add_part_response, upload_id, file_handle_id, status_first_call,
                                                    status_call, part, pre_signed_url_generator, parts):
    status_list = [uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()
    invalid_content_type = 1

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type") as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete:
        with pytest.raises(TypeError):
            multipart_upload_file(client, file_name, invalid_content_type)
        mock_exist.assert_not_called()
        mock_isdir.assert_not_called()
        mock_basename.assert_not_called()
        mock_getsize.assert_not_called()
        mock_guess_type.assert_not_called()
        mock_get_md5.assert_not_called()
        mock_get_status.assert_not_called()
        mock_get_pool.assert_not_called()
        mock_get_pre_signed_url.assert_not_called()
        mock_complete.assert_not_called()
        mock_map.assert_not_called()


def test_multipart_upload_file_path_does_not_exist(client, file_name, small_file_size, content_type, data, md5,
                                                   part_number, uploading_status, completed_status, pre_signed_url,
                                                   add_part_response, upload_id, file_handle_id, status_first_call,
                                                   status_call, part, pre_signed_url_generator, parts):
    status_list = [uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()

    with patch.object(os.path, "exists", return_value=False) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type") as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete:
        with pytest.raises(ValueError):
            multipart_upload_file(client, file_name, content_type)
        mock_exist.assert_called_once_with(file_name)
        mock_isdir.assert_not_called()
        mock_basename.assert_not_called()
        mock_getsize.assert_not_called()
        mock_guess_type.assert_not_called()
        mock_get_md5.assert_not_called()
        mock_get_status.assert_not_called()
        mock_get_pool.assert_not_called()
        mock_get_pre_signed_url.assert_not_called()
        mock_complete.assert_not_called()
        mock_map.assert_not_called()


def test_multipart_upload_file_path_is_dir(client, file_name, small_file_size, content_type, data, md5, part_number,
                                           uploading_status, completed_status, pre_signed_url, add_part_response,
                                           upload_id, file_handle_id, status_first_call, status_call,
                                           part, pre_signed_url_generator, parts):
    status_list = [uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=True) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type") as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete:
        with pytest.raises(ValueError):
            multipart_upload_file(client, file_name, content_type)
        mock_exist.assert_called_once_with(file_name)
        mock_isdir.assert_called_once_with(file_name)
        mock_basename.assert_not_called()
        mock_getsize.assert_not_called()
        mock_guess_type.assert_not_called()
        mock_get_md5.assert_not_called()
        mock_get_status.assert_not_called()
        mock_get_pool.assert_not_called()
        mock_get_pre_signed_url.assert_not_called()
        mock_complete.assert_not_called()
        mock_map.assert_not_called()


def test_multipart_upload_file_none_content_type(client, file_name, small_file_size, content_type, data, md5,
                                                 part_number, uploading_status, completed_status, pre_signed_url,
                                                 add_part_response, upload_id, file_handle_id, status_first_call,
                                                 status_call, part, pre_signed_url_generator, parts):
    status_list = [uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type", return_value=(content_type, None)) as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete, \
            patch('spccore.multipart_upload._upload_and_add_part',
                  return_value=add_part_response) as mock_upload_and_add_part, \
            patch('spccore.multipart_upload.get_part_data', return_value=data) as mock_get_part_data:
        assert file_handle_id == multipart_upload_file(client, file_name, None, pool_provider=pool_provider)
        mock_exist.assert_called_once_with(file_name)
        mock_isdir.assert_called_once_with(file_name)
        mock_basename.assert_called_once_with(file_name)
        mock_getsize.assert_called_once_with(file_name)
        mock_guess_type.assert_called_once_with(file_name, strict=False)
        mock_get_md5.assert_called_once_with(file_name)
        mock_get_status.assert_has_calls([status_first_call, status_call])
        mock_get_pool.assert_called_once_with()
        mock_get_pre_signed_url.assert_called_once_with(client, upload_id, content_type, parts)
        mock_complete.assert_called_once_with(client, upload_id)
        mock_map.assert_called_once_with(ANY, pre_signed_url_generator)
        args, _ = mock_map.call_args_list[0]
        one_chunk_upload_func, _ = args
        assert add_part_response == one_chunk_upload_func(part)
        mock_upload_and_add_part.assert_called_once_with(client, upload_id, part_number, pre_signed_url, data)
        mock_get_part_data.assert_called_once_with(file_name, part_number, SYNAPSE_DEFAULT_UPLOAD_PART_SIZE)


def test_multipart_upload_file_cannot_get_type(client, file_name, small_file_size, data, md5, part_number,
                                               uploading_status, completed_status, pre_signed_url,  add_part_response,
                                               upload_id, file_handle_id, part, pre_signed_url_generator, parts):
    status_list = [uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()
    content_type = OCTET_STREAM_CONTENT_TYPE
    status_first_call = call(client,
                             file_name,
                             content_type,
                             small_file_size,
                             md5,
                             storage_location_id=SYNAPSE_DEFAULT_STORAGE_LOCATION_ID,
                             generate_preview=False,
                             force_restart=False)
    status_call = call(client,
                       file_name,
                       content_type,
                       small_file_size,
                       md5,
                       storage_location_id=SYNAPSE_DEFAULT_STORAGE_LOCATION_ID,
                       generate_preview=False)

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type", return_value=(None, None)) as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete, \
            patch('spccore.multipart_upload._upload_and_add_part',
                  return_value=add_part_response) as mock_upload_and_add_part, \
            patch('spccore.multipart_upload.get_part_data', return_value=data) as mock_get_part_data:
        assert file_handle_id == multipart_upload_file(client, file_name, None, pool_provider=pool_provider)
        mock_exist.assert_called_once_with(file_name)
        mock_isdir.assert_called_once_with(file_name)
        mock_basename.assert_called_once_with(file_name)
        mock_getsize.assert_called_once_with(file_name)
        mock_guess_type.assert_called_once_with(file_name, strict=False)
        mock_get_md5.assert_called_once_with(file_name)
        mock_get_status.assert_has_calls([status_first_call, status_call])
        mock_get_pool.assert_called_once_with()
        mock_get_pre_signed_url.assert_called_once_with(client, upload_id, content_type, parts)
        mock_complete.assert_called_once_with(client, upload_id)
        mock_map.assert_called_once_with(ANY, pre_signed_url_generator)
        args, _ = mock_map.call_args_list[0]
        one_chunk_upload_func, _ = args
        assert add_part_response == one_chunk_upload_func(part)
        mock_upload_and_add_part.assert_called_once_with(client, upload_id, part_number, pre_signed_url, data)
        mock_get_part_data.assert_called_once_with(file_name, part_number, SYNAPSE_DEFAULT_UPLOAD_PART_SIZE)


def test_multipart_upload_file_one_chunk(client, file_name, small_file_size, content_type, data, md5, part_number,
                                         uploading_status, completed_status, pre_signed_url, add_part_response,
                                         upload_id, file_handle_id, status_first_call, status_call, part,
                                         pre_signed_url_generator, parts):
    status_list = [uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type") as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete, \
            patch('spccore.multipart_upload._upload_and_add_part',
                  return_value=add_part_response) as mock_upload_and_add_part, \
            patch('spccore.multipart_upload.get_part_data', return_value=data) as mock_get_part_data:
        assert file_handle_id == multipart_upload_file(client, file_name, content_type, pool_provider=pool_provider)
        mock_exist.assert_called_once_with(file_name)
        mock_isdir.assert_called_once_with(file_name)
        mock_basename.assert_called_once_with(file_name)
        mock_getsize.assert_called_once_with(file_name)
        mock_guess_type.assert_not_called()
        mock_get_md5.assert_called_once_with(file_name)
        mock_get_status.assert_has_calls([status_first_call, status_call])
        mock_get_pool.assert_called_once_with()
        mock_get_pre_signed_url.assert_called_once_with(client, upload_id, content_type, parts)
        mock_complete.assert_called_once_with(client, upload_id)
        mock_map.assert_called_once_with(ANY, pre_signed_url_generator)
        args, _ = mock_map.call_args_list[0]
        one_chunk_upload_func, _ = args
        assert add_part_response == one_chunk_upload_func(part)
        mock_upload_and_add_part.assert_called_once_with(client, upload_id, part_number, pre_signed_url, data)
        mock_get_part_data.assert_called_once_with(file_name, part_number, SYNAPSE_DEFAULT_UPLOAD_PART_SIZE)


def test_multipart_upload_file_with_retry(client, file_name, small_file_size, content_type, data, md5, part_number,
                                          uploading_status, completed_status, pre_signed_url, add_part_response,
                                          upload_id, file_handle_id, status_first_call, status_call, part,
                                          pre_signed_url_generator, parts):
    status_list = [uploading_status, uploading_status, completed_status]
    pool_provider = Mock()
    pool = Mock()

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type") as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete, \
            patch('spccore.multipart_upload._upload_and_add_part',
                  side_effect=(SynapseServerError(), add_part_response)) as mock_upload_and_add_part, \
            patch('spccore.multipart_upload.get_part_data', return_value=data) as mock_get_part_data:
        assert file_handle_id == multipart_upload_file(client, file_name, content_type, pool_provider=pool_provider)
        mock_exist.assert_called_once_with(file_name)
        mock_isdir.assert_called_once_with(file_name)
        mock_basename.assert_called_once_with(file_name)
        mock_getsize.assert_called_once_with(file_name)
        mock_guess_type.assert_not_called()
        mock_get_md5.assert_called_once_with(file_name)
        mock_get_status.assert_has_calls([status_first_call, status_call])
        mock_get_pool.assert_called_once_with()
        assert mock_get_pre_signed_url.call_args_list == [call(client, upload_id, content_type, parts),
                                                          call(client, upload_id, content_type, parts)]
        mock_complete.assert_called_once_with(client, upload_id)
        assert mock_map.call_args_list == [call(ANY, pre_signed_url_generator),
                                           call(ANY, pre_signed_url_generator)]
        args, _ = mock_map.call_args_list[0]
        one_chunk_upload_func, _ = args
        one_chunk_upload_func(part)
        args, _ = mock_map.call_args_list[1]
        one_chunk_upload_func, _ = args
        assert add_part_response == one_chunk_upload_func(part)
        assert mock_upload_and_add_part.call_args_list == [call(client, upload_id, part_number, pre_signed_url, data),
                                                           call(client, upload_id, part_number, pre_signed_url, data)]
        assert mock_get_part_data.call_args_list == [call(file_name, part_number, SYNAPSE_DEFAULT_UPLOAD_PART_SIZE),
                                                     call(file_name, part_number, SYNAPSE_DEFAULT_UPLOAD_PART_SIZE)]


def test_multipart_upload_file_failed(client, file_name, small_file_size, content_type, data, md5, part_number, parts,
                                      uploading_status, completed_status, pre_signed_url, add_part_response, upload_id,
                                      file_handle_id, status_first_call, status_call, part, pre_signed_url_generator):
    status_list = [uploading_status,
                   uploading_status,
                   uploading_status,
                   uploading_status,
                   uploading_status,
                   uploading_status]
    pool_provider = Mock()
    pool = Mock()

    with patch.object(os.path, "exists", return_value=True) as mock_exist, \
            patch.object(os.path, "isdir", return_value=False) as mock_isdir, \
            patch.object(os.path, "basename", return_value=file_name) as mock_basename, \
            patch.object(os.path, "getsize", return_value=small_file_size) as mock_getsize, \
            patch.object(mimetypes, "guess_type") as mock_guess_type, \
            patch('spccore.multipart_upload.get_md5_hex_digest_for_file', return_value=md5) as mock_get_md5, \
            patch('spccore.multipart_upload._multipart_upload_status', side_effect=status_list) as mock_get_status, \
            patch.object(pool_provider, "get_pool", return_value=pool) as mock_get_pool, \
            patch.object(pool, "map") as mock_map, \
            patch('spccore.multipart_upload._get_batch_pre_signed_url',
                  return_value=pre_signed_url_generator) as mock_get_pre_signed_url, \
            patch('spccore.multipart_upload._complete_multipart_upload',
                  return_value=completed_status) as mock_complete:
        with pytest.raises(SynapseClientError):
            multipart_upload_file(client, file_name, content_type, pool_provider=pool_provider)
        mock_exist.assert_called_once_with(file_name)
        mock_isdir.assert_called_once_with(file_name)
        mock_basename.assert_called_once_with(file_name)
        mock_getsize.assert_called_once_with(file_name)
        mock_guess_type.assert_not_called()
        mock_get_md5.assert_called_once_with(file_name)
        mock_get_status.assert_has_calls([status_first_call, status_call])
        mock_get_pool.assert_called_once_with()
        assert mock_get_pre_signed_url.call_args_list == [call(client, upload_id, content_type, parts),
                                                          call(client, upload_id, content_type, parts),
                                                          call(client, upload_id, content_type, parts),
                                                          call(client, upload_id, content_type, parts),
                                                          call(client, upload_id, content_type, parts)]
        mock_complete.assert_not_called()
        assert mock_map.call_args_list == [call(ANY, pre_signed_url_generator),
                                           call(ANY, pre_signed_url_generator),
                                           call(ANY, pre_signed_url_generator),
                                           call(ANY, pre_signed_url_generator),
                                           call(ANY, pre_signed_url_generator)]
        assert len(mock_map.call_args_list) == 5
