import pytest
from unittest.mock import patch, Mock

from spccore.baseclient import *
from spccore.exceptions import *
from spccore.baseclient import _enforce_user_agent, _handle_response, _generate_signed_headers, _generate_request_url


# _enforce_user_agent

def test__enforce_user_agent_empty():
    assert _enforce_user_agent(dict()) == SYNAPSE_USER_AGENT_HEADER


def test__enforce_user_agent_override():
    headers = {
        'User-Agent': requests.utils.default_user_agent()
    }
    assert _enforce_user_agent(headers)['User-Agent'] == SYNAPSE_USER_AGENT_HEADER['User-Agent']


def test__enforce_user_agent_does_not_effect_other_headers():
    headers = _enforce_user_agent(SYNAPSE_DEFAULT_HTTP_HEADERS)
    assert headers['User-Agent'] == SYNAPSE_USER_AGENT_HEADER['User-Agent']
    assert headers['content-type'] == SYNAPSE_DEFAULT_HTTP_HEADERS['content-type']
    assert headers['Accept'] == SYNAPSE_DEFAULT_HTTP_HEADERS['Accept']


# _handle_response

def test__handle_response_error():
    response = requests.Response()
    with patch('spccore.baseclient.check_status_code_and_raise_error',
               side_effect=SynapseBadRequestError()) as mock_check_status_func:
        with pytest.raises(SynapseBadRequestError):
            _handle_response(response)
        mock_check_status_func.assert_called_once_with(response)


def test__handle_response_none_content_type():
    response = Mock(requests.Response)
    response.headers = {}
    response.text = "some text"
    with patch('spccore.baseclient.check_status_code_and_raise_error') as mock_check_status_func:
        assert _handle_response(response) == response.text
        mock_check_status_func.assert_called_once_with(response)


def test__handle_response_with_plain_text_content_type():
    response = Mock(requests.Response)
    response.headers = {CONTENT_TYPE_HEADER: 'text/plain'}
    response.text = "some text"
    with patch('spccore.baseclient.check_status_code_and_raise_error') as mock_check_status_func:
        assert _handle_response(response) == response.text
        mock_check_status_func.assert_called_once_with(response)


def test__handle_response_with_json_content_type():
    response = Mock(requests.Response)
    response.headers = {CONTENT_TYPE_HEADER: JSON_CONTENT_TYPE}
    json = {'result': 'a'}
    with patch('spccore.baseclient.check_status_code_and_raise_error') as mock_check_status_func, \
            patch.object(response, "json", return_value=json):
        assert _handle_response(response) == json
        mock_check_status_func.assert_called_once_with(response)


# _generate_signed_headers

def test__generate_signed_headers_none_url():
    with pytest.raises(ValueError):
        _generate_signed_headers(None)


def test__generate_signed_headers_none_headers():
    headers = _generate_signed_headers("/abc")
    assert headers[CONTENT_TYPE_HEADER] == SYNAPSE_DEFAULT_HTTP_HEADERS[CONTENT_TYPE_HEADER]
    assert headers['Accept'] == SYNAPSE_DEFAULT_HTTP_HEADERS['Accept']
    assert headers['User-Agent'] == SYNAPSE_USER_AGENT_HEADER['User-Agent']


def test__generate_signed_headers_update_headers():
    headers = _generate_signed_headers("/abc", headers={'User-Agent': "a"})
    assert headers['User-Agent'] == SYNAPSE_USER_AGENT_HEADER['User-Agent']


def test__generate_signed_headers_with_no_username():
    headers = _generate_signed_headers("/abc", api_key=base64.b64encode(b"I am an api key"))
    assert headers.get(SYNAPSE_USER_ID_HEADER) is None
    assert headers.get(SYNAPSE_SIGNATURE_TIMESTAMP_HEADER) is None
    assert headers.get(SYNAPSE_SIGNATURE_HEADER) is None


def test__generate_signed_headers_with_no_api_key():
    headers = _generate_signed_headers("/abc", username="k")
    assert headers.get(SYNAPSE_USER_ID_HEADER) is None
    assert headers.get(SYNAPSE_SIGNATURE_TIMESTAMP_HEADER) is None
    assert headers.get(SYNAPSE_SIGNATURE_HEADER) is None


def test__generate_signed_headers_with_api_key():
    timestamp_str = "2019-06-25T23:12:43.000Z"
    with patch.object(time, "strftime", return_value=timestamp_str):
        headers = _generate_signed_headers("/abc", username="k", api_key=base64.b64encode(b"I am an api key"))
        assert headers.get(SYNAPSE_USER_ID_HEADER) == "k"
        assert headers.get(SYNAPSE_SIGNATURE_TIMESTAMP_HEADER) == timestamp_str
        assert headers.get(SYNAPSE_SIGNATURE_HEADER) == b'Kq3Q4E9md2jxG8lsvGvi9295Eh0='


# _generate_request_url

def test__generate_request_url_invalid_endpoint():
    with pytest.raises(ValueError):
        _generate_request_url(None, "/entity")


def test__generate_request_url_none_path():
    with pytest.raises(ValueError):
        _generate_request_url("https://synapse.org", None)

def test__generate_request_url_invalid_path():
    with pytest.raises(ValueError):
        _generate_request_url("https://synapse.org", "http:/path.com/path")


def test__generate_request_url():
    assert _generate_request_url("https://synapse.org", "/entity") == "https://synapse.org/entity"


# get_base_client

def test_get_base_client():
    repo_endpoint = "repo"
    auth_endpoint = "auth"
    file_endpoint = "file"
    username = "x"
    api_key = base64.b64encode(b"I am an api key").decode()
    client = get_base_client(repo_endpoint=repo_endpoint,
                             auth_endpoint=auth_endpoint,
                             file_endpoint=file_endpoint,
                             username=username,
                             api_key=api_key)
    assert client.default_repo_endpoint == repo_endpoint
    assert client.default_auth_endpoint == auth_endpoint
    assert client.default_file_endpoint == file_endpoint
    assert client._username == username
    assert client._api_key == base64.b64decode(api_key)
    assert client._requests_session is not None


# SynapseBaseClient

class TestSynapseBaseClient:

    def test_constructor(self):
        repo_endpoint = "repo"
        auth_endpoint = "auth"
        file_endpoint = "file"
        username = "x"
        api_key = base64.b64encode(b"I am an api key").decode()
        client = SynapseBaseClient(repo_endpoint=repo_endpoint,
                                   auth_endpoint=auth_endpoint,
                                   file_endpoint=file_endpoint,
                                   username=username,
                                   api_key=api_key)
        assert client.default_repo_endpoint == repo_endpoint
        assert client.default_auth_endpoint == auth_endpoint
        assert client.default_file_endpoint == file_endpoint
        assert client._username == username
        assert client._api_key == base64.b64decode(api_key)
        assert client._requests_session is not None

    @pytest.fixture
    def client_setup(self):
        username = 'x'
        api_key = base64.b64encode(b"I am an api key").decode()
        return username, api_key, SynapseBaseClient(username=username, api_key=api_key)

    @pytest.fixture
    def test_data(self):
        req_response = Mock(requests.Response)
        path = "/entity/syn123"
        headers = SYNAPSE_USER_AGENT_HEADER
        stub_response = {'id': 'syn123'}
        params = {'key': 'value'}
        return req_response, path, headers, stub_response, params

    # get

    def test_get_use_default_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, stub_response, params = test_data

        with patch.object(requests.Session, 'get', return_value=req_response) as mock_req_get, \
                patch('spccore.baseclient._handle_response', return_value=stub_response) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.get(path, request_parameters=params) == stub_response
            mock_req_get.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT+path, headers=headers, params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT+path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)

    def test_get_custom_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, stub_response, params = test_data
        endpoint = "https://repo-dev.dev.sagebase.org/repo/v1"

        with patch.object(requests.Session, 'get', return_value=req_response) as mock_req_get, \
                patch('spccore.baseclient._handle_response', return_value=stub_response) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.get(path, request_parameters=params, endpoint=endpoint) == stub_response
            mock_req_get.assert_called_once_with(endpoint+path, headers=headers, params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(endpoint+path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)

    # post

    def test_post_use_default_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, body, params = test_data

        with patch.object(requests.Session, 'post', return_value=req_response) as mock_req_post, \
                patch('spccore.baseclient._handle_response', return_value=body) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.post(path, request_body=body, request_parameters=params) == body
            mock_req_post.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT + path,
                                                  data=json.dumps(body),
                                                  headers=headers,
                                                  params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT + path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)

    def test_post_custom_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, body, params = test_data
        endpoint = "https://repo-dev.dev.sagebase.org/repo/v1"

        with patch.object(requests.Session, 'post', return_value=req_response) as mock_req_post, \
                patch('spccore.baseclient._handle_response', return_value=body) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.post(path, request_body=body, request_parameters=params, endpoint=endpoint) == body
            mock_req_post.assert_called_once_with(endpoint + path,
                                                  data=json.dumps(body),
                                                  headers=headers,
                                                  params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(endpoint + path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)

    # put

    def test_put_use_default_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, body, params = test_data

        with patch.object(requests.Session, 'put', return_value=req_response) as mock_req_put, \
                patch('spccore.baseclient._handle_response', return_value=body) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.put(path, request_body=body, request_parameters=params) == body
            mock_req_put.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT + path,
                                                 data=json.dumps(body),
                                                 headers=headers,
                                                 params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT + path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)

    def test_put_custom_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, body, params = test_data
        endpoint = "https://repo-dev.dev.sagebase.org/repo/v1"

        with patch.object(requests.Session, 'put', return_value=req_response) as mock_req_put, \
                patch('spccore.baseclient._handle_response', return_value=body) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.put(path, request_body=body, request_parameters=params, endpoint=endpoint) == body
            mock_req_put.assert_called_once_with(endpoint + path,
                                                 data=json.dumps(body),
                                                 headers=headers,
                                                 params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(endpoint + path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)

    # delete

    def test_delete_use_default_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, stub_response, params = test_data

        with patch.object(requests.Session, 'delete', return_value=req_response) as mock_req_delete, \
                patch('spccore.baseclient._handle_response', return_value=stub_response) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.delete(path, request_parameters=params) == stub_response
            mock_req_delete.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT+path, headers=headers, params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(SYNAPSE_DEFAULT_REPO_ENDPOINT+path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)

    def test_delete_custom_endpoint(self, client_setup, test_data):
        username, api_key, client = client_setup
        req_response, path, headers, stub_response, params = test_data
        endpoint = "https://repo-dev.dev.sagebase.org/repo/v1"

        with patch.object(requests.Session, 'delete', return_value=req_response) as mock_req_delete, \
                patch('spccore.baseclient._handle_response', return_value=stub_response) as mock_handle, \
                patch('spccore.baseclient._generate_signed_headers', return_value=headers) as mock_sign_headers, \
                patch.object(req_response, "json", return_value=json):
            assert client.delete(path, request_parameters=params, endpoint=endpoint) == stub_response
            mock_req_delete.assert_called_once_with(endpoint+path, headers=headers, params=params)
            mock_handle.assert_called_once_with(req_response)
            mock_sign_headers.assert_called_once_with(endpoint+path,
                                                      username=username,
                                                      api_key=base64.b64decode(api_key),
                                                      headers=None)
