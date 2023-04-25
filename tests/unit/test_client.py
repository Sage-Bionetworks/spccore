"""Test client"""
from unittest.mock import patch, Mock

import pytest
import requests  # type: ignore

from spccore import client
from spccore.exceptions import (
    SynapseBadRequestError,
)
from spccore.constants import (
    CONTENT_TYPE_HEADER,
    JSON_CONTENT_TYPE,
    SYNAPSE_USER_AGENT_HEADER,
    SYNAPSE_DEFAULT_REPO_ENDPOINT,
)
from spccore.client import _handle_response, _generate_request_url, SynapseBaseClient


def test__handle_response_error():
    """Test handling response error"""
    response = requests.Response()
    with patch.object(
        client,
        "check_status_code_and_raise_error",
        side_effect=SynapseBadRequestError(),
    ) as mock_check_status_func, pytest.raises(SynapseBadRequestError):
        _handle_response(response)
        mock_check_status_func.assert_called_once_with(response)


def test__handle_response_none_content_type():
    """Test handling response content type"""
    response = Mock(requests.Response)
    response.headers = {}
    response.text = "some text"
    with patch.object(
        client, "check_status_code_and_raise_error"
    ) as mock_check_status_func:
        assert _handle_response(response) == response.text
        mock_check_status_func.assert_called_once_with(response)


def test__handle_response_with_plain_text_content_type():
    response = Mock(requests.Response)
    response.headers = {CONTENT_TYPE_HEADER: "text/plain"}
    response.text = "some text"
    with patch.object(
        client, "check_status_code_and_raise_error"
    ) as mock_check_status_func:
        assert _handle_response(response) == response.text
        mock_check_status_func.assert_called_once_with(response)


def test__handle_response_with_json_content_type():
    response = Mock(requests.Response)
    response.headers = {CONTENT_TYPE_HEADER: JSON_CONTENT_TYPE}
    json = {"result": "a"}
    with patch.object(
        client, "check_status_code_and_raise_error"
    ) as mock_check_status_func, patch.object(response, "json", return_value=json):
        assert _handle_response(response) == json
        mock_check_status_func.assert_called_once_with(response)


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
    assert (
        _generate_request_url("https://synapse.org", "/entity")
        == "https://synapse.org/entity"
    )


class TestSynapseBaseClient:
    """Test base client"""

    @pytest.fixture
    def client_setup(self):
        class TestClient(SynapseBaseClient):
            pass

        auth_token = "I am a test token"
        return auth_token, TestClient(auth_token=auth_token)

    @pytest.fixture
    def test_data(self):
        req_response = Mock(requests.Response)
        path = "/entity/syn123"
        headers = SYNAPSE_USER_AGENT_HEADER
        stub_response = {"id": "syn123"}
        params = {"key": "value"}
        return req_response, path, headers, stub_response, params

    # get
    @patch.object(requests.Session, "get")
    @patch.object(client, "_handle_response")
    def test_get_use_default_endpoint(
        self, mock_handle, mock_req_get, client_setup, test_data
    ):
        auth_token, tc = client_setup
        req_response, path, headers, stub_response, params = test_data
        mock_req_get.return_value = req_response
        mock_handle.return_value = stub_response

        with patch.object(req_response, "json", return_value={}):
            assert tc.rest_get(path, query_parameters=params) == stub_response
            mock_req_get.assert_called_once_with(
                SYNAPSE_DEFAULT_REPO_ENDPOINT + path, params=params
            )
            mock_handle.assert_called_once_with(response=req_response)

    @patch.object(requests.Session, "get")
    @patch.object(client, "_handle_response")
    def test_get_custom_endpoint(
        self, mock_handle, mock_req_get, client_setup, test_data
    ):
        auth_token, tc = client_setup
        req_response, path, headers, stub_response, params = test_data
        endpoint = "https://repo-dev.dev.sagebase.org/repo/v1"
        mock_req_get.return_value = req_response
        mock_handle.return_value = stub_response

        with patch.object(req_response, "json", return_value={}):
            assert (
                tc.rest_get(path, server_url=endpoint, query_parameters=params)
                == stub_response
            )
            mock_req_get.assert_called_once_with(endpoint + path, params=params)
            mock_handle.assert_called_once_with(response=req_response)

    # # post
    # The patches closet to the function has to be first
    @patch.object(requests.Session, "get")
    @patch.object(client, "_handle_response")
    def test_post_use_default_endpoint(
        self, mock_handle, mock_req_get, client_setup, test_data
    ):
        auth_token, tc = client_setup
        req_response, path, headers, body, params = test_data
        mock_req_get.return_value = req_response
        mock_handle.return_value = body

        with patch.object(req_response, "json", return_value={}):
            assert tc.rest_get(path, query_parameters=params, data=body) == body
            mock_req_get.assert_called_once_with(
                SYNAPSE_DEFAULT_REPO_ENDPOINT + path, params=params, data=body
            )
            mock_handle.assert_called_once_with(response=req_response)
