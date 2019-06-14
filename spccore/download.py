class DownloadRequest:
    """
    A request to download a file from Synapse

    ...

    Attributes
    ----------
    file_handle_id : int
        The file handle ID to download.
    object_id : str
        The Synapse object this file associated to.
    object_type : str
        the type of the associated Synapse object.
    path : str
        The local path to download the file to.
        This path can be either absolute path or relative path from where the code is executed to the download location.
    """

    file_handle_id = 0
    object_id = ""
    object_type = ""
    path = ""


    def __init__(self, file_handle_id: int, object_id: str, object_type: str, path: str):
        """

        :param file_handle_id:
        :param object_id:
        :param object_type:
        :param path:
        """

        self.file_handle_id = file_handle_id
        self.object_id = object_id
        self.object_type = object_type
        self.path = path


