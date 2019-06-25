import pytest
from unittest.mock import patch, Mock

from spccore.baseclient import *
from spccore.exceptions import *
from spccore.baseclient import _enforce_user_agent, _handle_response


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


# _generate_request_url


# get_base_client


# SynapseBaseClient