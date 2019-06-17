import base64
import hashlib
import hmac
import requests
import time
import typing
import urllib.parse as urllib_parse
from .constants import *
from .download import *
from .exceptions import *


class SynapseConnection:
    """
    A connection to Synapse backend.

    ...

    Attributes
    ----------
    base_endpoint : str
        the Synapse server base endpoint
    username: str
        the user's username
    api_key : str
        the user's credentials
    session : requests.Session
        a requests' Session

    Methods
    -------
    rest_get("/entity/syn123", request_parameters={})
        Performs an HTTP GET request

    rest_put("/entity/syn123", {id="syn123"}, request_parameters={})
        Performs an HTTP PUT request

    rest_post("/entity", {name="new_folder"}, request_parameters={})
        Performs an HTTP POST request

    rest_delete("/entity/syn123", request_parameters={})
        Performs an HTTP DELETE request

    upload_file_handle("/path/to/analysis.txt", content_type="text/plain", generate_preview=False)
        Uploads a file to Synapse

    download_file_handles({file_handle_id="456",
                         object_id="syn123",
                         object_type="FileEntity",
                         path="~/Documents/analysis.txt"})
        Downloads a batch of files from Synapse

    """

    def __init__(self, *,
                 base_endpoint: str = SYNAPSE_DEFAULT_BASE_ENDPOINT,
                 username: str = None,
                 api_key: str = None):
        """

        :param base_endpoint: the Synapse server base endpoint
        :param username: the Synapse username
        :param api_key: the Synapse API key
        """
        self.base_endpoint = base_endpoint
        self.username = username
        self.api_key = api_key
        self.session = requests.Session()

    def rest_get(self,
                 request_path: str,
                 *,
                 request_parameters: dict = {}
                 ) -> typing.Union[dict, str]:
        """
        Performs an HTTP GET request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_parameters: path parameters to include in this request
        :return: the response body of the request
        """
        url = _generate_request_url(self.base_endpoint, request_path)
        return _handle_response(self.session.get(url,
                                                 headers=_generate_signed_headers(url),
                                                 params=request_parameters))

    def rest_put(self,
                 request_path: str,
                 request_body: dict,
                 *,
                 request_parameters: dict = {}
                 ) -> typing.Union[dict, str]:
        """
        Performs an HTTP PUT request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_body: the request body
        :param request_parameters: path parameters to include in this request
        :return: the response body of the request
        """
        url = _generate_request_url(self.base_endpoint, request_path)
        return _handle_response(self.session.put(url,
                                                 data=request_body,
                                                 headers=_generate_signed_headers(url),
                                                 params=request_parameters))

    def rest_post(self,
                  request_path: str,
                  request_body: dict,
                  *,
                  request_parameters: dict = {}
                  ) -> typing.Union[dict, str]:
        """
        Performs an HTTP POST request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_body: the request body
        :param request_parameters: path parameters to include in this request
        :return: the response body of the request
        """
        url = _generate_request_url(self.base_endpoint, request_path)
        return _handle_response(self.session.post(url,
                                                 data=request_body,
                                                 headers=_generate_signed_headers(url),
                                                 params=request_parameters))

    def rest_delete(self,
                    request_path: str,
                    *,
                    request_parameters: dict = {}
                    ) -> typing.Union[dict, str]:
        """
        Performs an HTTP DELETE request

        :param request_path: the unique path in the URI of the resource (i.e. "/entity/syn123")
        :param request_parameters: path parameters to include in this request
        :return: the response body of the request
        """
        url = _generate_request_url(self.base_endpoint, request_path)
        return _handle_response(self.session.delete(url,
                                                    headers=_generate_signed_headers(url),
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
                              requests: typing.Sequence[DownloadRequest],
                              *,
                              use_multiple_threads: bool = True
                              ) -> typing.Mapping[DownloadRequest, DownloadResult]:
        """
        Downloads a batch of files from Synapse

        :param requests: the list of download requests
        :param use_multiple_threads: set to False to use single thread. Default True.
        :return: a map between the DownloadRequest and the result
        """


ANONYMOUS_CONNECTION = SynapseConnection()


def get_connection(*,
                   base_endpoint: str = SYNAPSE_DEFAULT_BASE_ENDPOINT,
                   username: str = None,
                   api_key: str = None
                   ) -> SynapseConnection:
    """
    Get a connection to the Synapse server

    :param base_endpoint: the Synapse server base endpoint
    :param username: the Synapse username
    :param api_key: the Synapse API key
    :return: a Synapse connection
    """
    if username is None or api_key is None:
        return ANONYMOUS_CONNECTION
    return SynapseConnection(base_endpoint=base_endpoint, username=username, api_key=api_key)


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
        raise ValueError("Incorrect format for request_path: %(request_path)" % {'request_path': request_path})
    return endpoint + request_path


def _generate_signed_headers(url: str, username: str, api_key: str, *, headers: dict = None) -> dict:
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

    if username is None or api_key is None:
        return headers

    sig_timestamp = time.strftime(ISO_FORMAT, time.gmtime())
    url = urllib_parse.urlparse(url).path
    sig_data = username + url + sig_timestamp
    signature = base64.b64encode(hmac.new(api_key, sig_data.encode('utf-8'), hashlib.sha1).digest())

    headers.update({SYNAPSE_USER_ID_HEADER: username,
                    SYNAPSE_SIGNATURE_TIMESTAMP_HEADER: sig_timestamp,
                    SYNAPSE_SIGNATURE_HEADER: signature})
    return headers


def _handle_response(response: requests.Response) -> dict:
    """
    Handle the requests' Response

    :param response: the response returned from requests
    :return: the response body
    """
    check_status_code_and_raise_error(response)
    content_type = response.headers.get(CONTENT_TYPE_HEADER, None)
    if content_type.lower().strip().startswith(JSON_CONTENT_TYPE):
        return response.json()
    else:
        return response.text


