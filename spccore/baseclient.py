import base64
import hashlib
import hmac
import json
import time
import typing
import urllib.parse as urllib_parse
from .constants import *
from .download import *
from .exceptions import *
from .utils import *


class SynapseBaseClient:
    """
    A base client object that manages a connection to the Synapse backend.

    ...

    Methods
    -------
    get("/entity/syn123", request_parameters={})
        Performs an HTTP GET request

    put("/entity/syn123", {id="syn123"}, request_parameters={})
        Performs an HTTP PUT request

    post("/entity", {name="new_folder"}, request_parameters={})
        Performs an HTTP POST request

    delete("/entity/syn123", request_parameters={})
        Performs an HTTP DELETE request

    upload_file_handle("/path/to/analysis.txt", content_type="text/plain", generate_preview=False)
        Uploads a file to Synapse

    download_file_handles(download_requests={file_handle_id="456",
                                             object_id="syn123",
                                             object_type="FileEntity",
                                             path="~/Documents/analysis.txt"})
        Downloads a batch of files from Synapse

    """

    def __init__(self, *,
                 repo_endpoint: str = SYNAPSE_DEFAULT_REPO_ENDPOINT,
                 auth_endpoint: str = SYNAPSE_DEFAULT_AUTH_ENDPOINT,
                 file_endpoint: str = SYNAPSE_DEFAULT_FILE_ENDPOINT,
                 username: str = None,
                 api_key: str = None):
        """

        :param repo_endpoint: the Synapse server repo endpoint
        :param auth_endpoint: the Synapse server auth endpoint
        :param file_endpoint: the Synapse server file endpoint
        :param username: the Synapse username
        :param api_key: the Synapse API key
        """
        validate_type(str, repo_endpoint, "repo_endpoint")
        validate_type(str, auth_endpoint, "auth_endpoint")
        validate_type(str, file_endpoint, "file_endpoint")
        validate_type(str, username, "username")
        validate_type(str, api_key, "api_key")

        self._default_repo_endpoint = repo_endpoint
        self._default_auth_endpoint = auth_endpoint
        self._default_file_endpoint = file_endpoint
        self._username = username
        self._api_key = base64.b64decode(api_key) if api_key is not None else None
        self._requests_session = requests.Session()

    def get(self,
            request_path: str,
            *,
            request_parameters: dict = None,
            endpoint: str = None,
            headers: dict = None
            ) -> typing.Union[dict, str]:
        """
        Performs an HTTP GET request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_parameters: path parameters to include in this request
        :param endpoint: the Synapse server endpoint
        :param headers: the HTTP headers
        :return: the response body of the request
        """
        if endpoint is None:
            endpoint = self._default_repo_endpoint
        url = _generate_request_url(endpoint, request_path)
        return _handle_response(self._requests_session.get(url,
                                                           headers=_generate_signed_headers(url,
                                                                                            username=self._username,
                                                                                            api_key=self._api_key,
                                                                                            headers=headers),
                                                           params=request_parameters))

    def put(self,
            request_path: str,
            request_body: dict,
            *,
            request_parameters: dict = None,
            endpoint: str = None,
            headers: dict = None
            ) -> typing.Union[dict, str]:
        """
        Performs an HTTP PUT request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_body: the request body
        :param request_parameters: path parameters to include in this request
        :param endpoint: the Synapse server endpoint
        :param headers: the HTTP headers
        :return: the response body of the request
        """
        if endpoint is None:
            endpoint = self._default_repo_endpoint
        url = _generate_request_url(endpoint, request_path)
        return _handle_response(self._requests_session.put(url,
                                                           data=json.dumps(request_body),
                                                           headers=_generate_signed_headers(url,
                                                                                            username=self._username,
                                                                                            api_key=self._api_key,
                                                                                            headers=headers),
                                                           params=request_parameters))

    def post(self,
             request_path: str,
             request_body: dict,
             *,
             request_parameters: dict = None,
             endpoint: str = None,
             headers: dict = None
             ) -> typing.Union[dict, str]:
        """
        Performs an HTTP POST request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_body: the request body
        :param request_parameters: path parameters to include in this request
        :param endpoint: the Synapse server endpoint
        :param headers: the HTTP headers
        :return: the response body of the request
        """
        if endpoint is None:
            endpoint = self._default_repo_endpoint
        url = _generate_request_url(endpoint, request_path)
        return _handle_response(self._requests_session.post(url,
                                                            data=json.dumps(request_body),
                                                            headers=_generate_signed_headers(url,
                                                                                             username=self._username,
                                                                                             api_key=self._api_key,
                                                                                             headers=headers),
                                                            params=request_parameters))

    def delete(self,
               request_path: str,
               *,
               request_parameters: dict = None,
               endpoint: str = None,
               headers: dict = None
               ) -> typing.Union[dict, str]:
        """
        Performs an HTTP DELETE request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_parameters: path parameters to include in this request
        :param endpoint: the Synapse server endpoint
        :param headers: the HTTP headers
        :return: the response body of the request
        """
        if endpoint is None:
            endpoint = self._default_repo_endpoint
        url = _generate_request_url(endpoint, request_path)
        return _handle_response(self._requests_session.delete(url,
                                                              headers=_generate_signed_headers(url,
                                                                                               username=self._username,
                                                                                               api_key=self._api_key,
                                                                                               headers=headers),
                                                              params=request_parameters))

    def upload_file_handle(self,
                           path: str,
                           content_type: str,
                           *,
                           generate_preview: bool = False,
                           storage_location_id: int = SYNAPSE_DEFAULT_STORAGE_LOCATION_ID,
                           use_multiple_threads: bool = True) -> dict:
        """
        Uploads a file to Synapse

        :param path: the absolute/relative path to the local file to be uploaded
        :param content_type: the content type of the file
        :param generate_preview: set to True to generate preview. Default False.
        :param storage_location_id: the ID of the Storage Location to upload to.
            Default SYNAPSE_DEFAULT_STORAGE_LOCATION_ID
        :param use_multiple_threads: set to False to use single thread. Default True.
        :return: the File Handle created in Synapse
        """

    def download_file_handles(self,
                              download_requests: typing.Sequence[DownloadRequest],
                              *,
                              use_multiple_threads: bool = True
                              ) -> typing.Mapping[DownloadRequest, DownloadResult]:
        """
        Downloads a batch of files from Synapse

        :param download_requests: the list of download requests
        :param use_multiple_threads: set to False to use single thread. Default True.
        :return: a map between the DownloadRequest and the result
        """


def get_base_client(*,
                    repo_endpoint: str = SYNAPSE_DEFAULT_REPO_ENDPOINT,
                    auth_endpoint: str = SYNAPSE_DEFAULT_AUTH_ENDPOINT,
                    file_endpoint: str = SYNAPSE_DEFAULT_FILE_ENDPOINT,
                    username: str = None,
                    api_key: str = None
                    ) -> SynapseBaseClient:
    """
    Get the base Synapse client.
    If username and api_key are provided, the client will sign all request using the provided api_key.
    Otherwise, all requests will be sent anonymously.

    :param repo_endpoint: the Synapse server repo endpoint
    :param auth_endpoint: the Synapse server auth endpoint
    :param file_endpoint: the Synapse server file endpoint
    :param username: the Synapse username
    :param api_key: the Synapse API key
    :return: a Synapse connection
    """
    return SynapseBaseClient(repo_endpoint=repo_endpoint,
                             auth_endpoint=auth_endpoint,
                             file_endpoint=file_endpoint,
                             username=username,
                             api_key=api_key)


# Helper functions

def _generate_request_url(endpoint: str, request_path: str) -> str:
    """
    Generate the URL for the HTTP request

    :param endpoint: the Synapse base endpoint
    :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
    :return: the URI of the resource
    """
    if endpoint is None or request_path is None:
        raise ValueError("endpoint and request_path are required.")
    if urllib_parse.urlparse(request_path).path != request_path:
        raise ValueError('Incorrect format for request_path: {request_path}'.format(**{'request_path': request_path}))
    return endpoint + request_path


def _generate_signed_headers(url: str,
                             *,
                             username: str = None,
                             api_key: bytes = None,
                             headers: dict = None
                             ) -> dict:
    """
    Generate headers signed with the API key

    :param url: the URL used in the HTTP request
    :param username: the user's username to sign the request
    :param api_key: the user's API key to sign the request
    :param headers: the HTTP request headers
    :return: the signed headers
    """

    if url is None:
        raise ValueError("url is required.")
    if headers is None:
        headers = dict(SYNAPSE_DEFAULT_HTTP_HEADERS)

    headers = _enforce_user_agent(headers)

    if username is None or api_key is None:
        return headers

    sig_timestamp = time.strftime(ISO_FORMAT, time.gmtime())
    url = urllib_parse.urlparse(url).path
    sig_data = username + url + sig_timestamp
    signature = base64.b64encode(hmac.new(api_key,
                                          sig_data.encode('utf-8'),
                                          hashlib.sha1).digest())
    headers.update({SYNAPSE_USER_ID_HEADER: username,
                    SYNAPSE_SIGNATURE_TIMESTAMP_HEADER: sig_timestamp,
                    SYNAPSE_SIGNATURE_HEADER: signature})
    return headers


def _handle_response(response: requests.Response) -> typing.Union[dict, str]:
    """
    Handle the requests' Response

    :param response: the response returned from requests
    :return: the response body
    """
    check_status_code_and_raise_error(response)
    content_type = response.headers.get(CONTENT_TYPE_HEADER, None)
    if content_type is not None and content_type.lower().strip().startswith(JSON_CONTENT_TYPE):
        return response.json()
    else:
        return response.text


def _enforce_user_agent(headers: dict) -> dict:
    """
    Update the headers to include User-Agent header that capture the core client

    :param headers: the HTTP headers to update
    :return: the HTTP headers with the core client as User-Agent
    """
    headers.update(SYNAPSE_USER_AGENT_HEADER)
    return headers
