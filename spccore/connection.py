from .constants import *
from .download import *

class SynapseConnection:
    """
    A connection to Synapse backend.

    ...

    Attributes
    ----------
    says_str : str
        a formatted string to print out what the animal says
    name : str
        the name of the animal
    sound : str
        the sound that the animal makes
    num_legs : int
        the number of legs the animal has (default 4)

    Methods
    -------
    rest_get("/entity/syn123", request_parameters={})
        Performs a REST GET request

    rest_put("/entity/syn123", {id="syn123"}, request_parameters={})
        Performs a REST PUT request

    rest_post("/entity", {name="new file"}, request_parameters={})
        Performs a REST POST request

    rest_delete("/entity/syn123", request_parameters={})
        Performs a REST DELETE request

    upload_file_handle("/path/to/analysis.txt", content_type="text/plain", generate_preview=False)
        Uploads a file to Synapse

    download_file_handles({file_handle_id="456",
                         object_id="syn123",
                         object_type="FileEntity",
                         path="~/Documents/analysis.txt"})
        Downloads a batch of files from Synapse

    """

    def __init__(self, *,
                 base_endpoint: str = DEFAULT_BASE_ENDPOINT,
                 username: str = None,
                 password: str = None,
                 api_key: str = None):
        """

        :param base_endpoint:
        :param username:
        :param password:
        :param api_key:
        """



    def rest_get(self, request_path: str, *, request_parameters: dict = {}) -> dict:
        """
        Performs a REST GET request

        :param request_path:
        :param request_parameters:
        :return:
        """


    def rest_put(self, request_path: str, request_body: dict, *, request_parameters: dict = {}) -> dict:
        """
        Performs a REST PUT request

        :param request_path:
        :param request_body:
        :param request_parameters:
        :return:
        """


    def rest_post(self, request_path: str, request_body: dict, *, request_parameters: dict = {}) -> dict:
        """
        Performs a REST POST request

        :param request_path:
        :param request_body:
        :param request_parameters:
        :return:
        """


    def rest_delete(self, request_path: str, *, request_parameters: dict = {}) -> None:
        """
        Performs a REST DELETE request

        :param request_path:
        :param request_parameters:
        :return:
        """


    def upload_file_handle(self,
                           path: str,
                           content_type: str,
                           generate_preview: bool,
                           *,
                           storage_location_id: int = 1,
                           use_multiple_threads: bool = True) -> dict:
        """
        Uploads a file to Synapse

        :param path:
        :param content_type:
        :param generate_preview:
        :param storage_location_id:
        :param use_multiple_threads:
        :return:
        """



    def download_file_handles(self,
                              requests : list[DownloadRequest],
                              *,
                              use_multiple_threads: bool = True) -> dict:
        """
        Downloads a batch of files from Synapse

        :param requests:
        :param use_multiple_threads:
        :return:
        """
