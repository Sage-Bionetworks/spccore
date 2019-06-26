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
    with patch('spccore.baseclient.check_status_code_and_raise_error', side_effect = SynapseBadRequestError()), \
         pytest.raises(SynapseBadRequestError):
        _handle_response(requests.Response())


def test__handle_response_none_content_type():
    response = Mock(requests.Response)
    response.headers = {}
    response.text = "some text"
    with patch('spccore.baseclient.check_status_code_and_raise_error'):
        assert _handle_response(response) == response.text


def test__handle_response_with_plain_text_content_type():
    response = Mock(requests.Response)
    response.headers = {CONTENT_TYPE_HEADER: 'text/plain'}
    response.text = "some text"
    with patch('spccore.baseclient.check_status_code_and_raise_error'):
        assert _handle_response(response) == response.text


def test__handle_response_with_json_content_type():
    response = Mock(requests.Response)
    response.headers = {CONTENT_TYPE_HEADER: JSON_CONTENT_TYPE}
    json = {'result': 'a'}
    with patch('spccore.baseclient.check_status_code_and_raise_error'), \
            patch.object(response, "json", return_value=json):
        assert _handle_response(response) == json


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


def test__generate_request_url_invalid_endpoint():
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
    assert client._default_repo_endpoint == repo_endpoint
    assert client._default_auth_endpoint == auth_endpoint
    assert client._default_file_endpoint == file_endpoint
    assert client._username == username
    assert client._api_key == base64.b64decode(api_key)
    assert client._requests_session is not None


# SynapseBaseClient
