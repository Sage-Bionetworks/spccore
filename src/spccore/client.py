"""Synapse base client"""
from abc import ABC
from typing import Optional, Union
import urllib.parse as urllib_parse

import requests  # type: ignore

from spccore.constants import (
    # SYNAPSE_DEFAULT_FILE_ENDPOINT,
    SYNAPSE_DEFAULT_REPO_ENDPOINT,
    CONTENT_TYPE_HEADER,
    JSON_CONTENT_TYPE,
    SYNAPSE_USER_AGENT_HEADER,
)
from spccore.exceptions import check_status_code_and_raise_error
from spccore.models.base_model import SynapseModel


def _generate_request_url(server_url: str, endpoint_path: str) -> str:
    """Generate the URL for the HTTP request

    Args:
        server_url (str): the Synapse base endpoint
        endpoint_path (str): the unique endpoint path of the resource
                             (i.e. "/entity/syn123")

    Raises:
        ValueError: when one or more parameters have invalid value

    Returns:
        str: the URI of the resource
    """
    if server_url is None or endpoint_path is None:
        raise ValueError("server_url and endpoint_path are required.")
    if urllib_parse.urlparse(endpoint_path).path != endpoint_path:
        raise ValueError(f"Incorrect format for endpoint_path: {endpoint_path}")
    return server_url + endpoint_path


def _handle_response(response: requests.Response) -> Union[dict, str]:
    """Handle the reqeusts' Response

    Args:
        response (requests.Response): Response returned from requests

    Returns:
        Union[dict, str]: The response body

    Raises:
        SynapseClientError: please see each error message
    """
    check_status_code_and_raise_error(response)
    content_type = response.headers.get(CONTENT_TYPE_HEADER, None)
    if content_type is not None and content_type.lower().strip().startswith(
        JSON_CONTENT_TYPE
    ):
        return response.json()
    else:
        return response.text


class SynapseBaseClient(ABC):
    """ABC meta class"""

    def __init__(self, auth_token: Optional[str] = None, profile: Optional[str] = None):
        self.auth_token = auth_token
        self.profile = profile

    @property
    def session(self) -> requests.Session:
        """Create Synapse Session

        Returns:
            requests.Session: An authenticated Synapse session
        """
        sess = requests.Session()
        sess.headers.update(SYNAPSE_USER_AGENT_HEADER)
        if self.auth_token is not None:
            sess.headers.update({"Authorization": f"Bearer {self.auth_token}"})
        return sess

    def rest_get(
        self,
        endpoint_path: str,
        server_url: Optional[str] = None,
        query_parameters: Optional[dict] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """Performs a HTTP Get request

        Args:
            endpoint_path (str): the unique path in the URI of the resource
                                 (i.e. "/entity/syn123")
            server_url (str): The Synapse server endpoint.
                              Defaults to None.
            query_parameters (dict): path parameters to include in this request

        Returns:
            dict, str: the response body of the request

        Raises:
            SynapseClientError: please see each error message
        """
        if server_url is None:
            server_url = SYNAPSE_DEFAULT_REPO_ENDPOINT

        url = _generate_request_url(server_url, endpoint_path)
        # TODO: Add logger debug to print url
        resp = self.session.get(url, params=query_parameters, **kwargs)
        # TODO: Add logger debug to print resp
        return _handle_response(response=resp)

    def rest_put(
        self,
        endpoint_path: str,
        server_url: Optional[str] = None,
        query_parameters: Optional[dict] = None,
        request_body: Optional[dict] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """Performs a HTTP Put request

        Args:
            endpoint_path (str): the unique path in the URI of the resource
                                 (i.e. "/entity/syn123")
            server_url (str): The Synapse server endpoint.
                              Defaults to None.
            query_parameters (dict): path parameters to include in this request
            request_body (dict): The request body

        Returns:
            dict, str: the response body of the request

        Raises:
            SynapseClientError: please see each error message
        """
        if server_url is None:
            server_url = SYNAPSE_DEFAULT_REPO_ENDPOINT

        url = _generate_request_url(server_url, endpoint_path)
        # TODO: Add logger debug to print url
        resp = self.session.put(
            url, params=query_parameters, data=request_body, **kwargs
        )
        # TODO: Add logger debug to print resp
        return _handle_response(response=resp)

    def rest_post(
        self,
        endpoint_path: str,
        server_url: Optional[str] = None,
        query_parameters: Optional[dict] = None,
        request_body: Optional[dict] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """Performs a HTTP Post request

        Args:
            endpoint_path (str): the unique path in the URI of the resource
                                 (i.e. "/entity/syn123")
            server_url (str): The Synapse server endpoint.
                              Defaults to None.
            query_parameters (dict): path parameters to include in this request
            request_body (dict): The request body

        Returns:
            dict, str: the response body of the request

        Raises:
            SynapseClientError: please see each error message
        """
        if server_url is None:
            server_url = SYNAPSE_DEFAULT_REPO_ENDPOINT

        url = _generate_request_url(server_url, endpoint_path)
        # TODO: Add logger debug to print url
        resp = self.session.post(
            url, params=query_parameters, data=request_body, **kwargs
        )
        # TODO: Add logger debug to print resp
        return _handle_response(response=resp)

    def rest_delete(
        self,
        endpoint_path: str,
        server_url: Optional[str] = None,
        query_parameters: Optional[dict] = None,
        **kwargs,
    ) -> Union[dict, str]:
        """Performs a HTTP Delete request

        Args:
            endpoint_path (str): the unique path in the URI of the resource
                                 (i.e. "/entity/syn123")
            server_url (str): The Synapse server endpoint.
                              Defaults to None.
            query_parameters (dict): path parameters to include in this request

        Returns:
            dict, str: the response body of the request

        Raises:
            SynapseClientError: please see each error message
        """
        if server_url is None:
            server_url = SYNAPSE_DEFAULT_REPO_ENDPOINT

        url = _generate_request_url(server_url, endpoint_path)
        # TODO: Add logger debug to print url
        resp = self.session.delete(url, params=query_parameters, **kwargs)
        # TODO: Add logger debug to print resp
        return _handle_response(response=resp)


class SynapseClient(SynapseBaseClient):
    """Synapse client"""

    def get(self, model: SynapseModel):
        """_summary_

        Args:
            synapse_model (_type_): _description_
        """
        response = self.rest_get(endpoint_path=model._get_url())
        if isinstance(response, dict):
            return model.from_kwargs(**response)
        else:
            return response

    def store(self, model: SynapseModel):
        "dataclasses.asdict(team)"
        pass
