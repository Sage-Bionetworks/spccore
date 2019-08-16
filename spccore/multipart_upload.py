import _hashlib
import json
import mimetypes
import os
import typing

import requests

from .constants import SYNAPSE_DEFAULT_STORAGE_LOCATION_ID
from .internal.fileutils import *
from .utils import *


DEFAULT_UPLOAD_PART_SIZE = 0




# Synapse API calls to perform multipart upload
################################################

def _multipart_upload_status(client,
                             file_name: str,
                             content_type: str,
                             file_size_byte: int,
                             md5: _hashlib.HASH,
                             *,
                             storage_location_id: int = SYNAPSE_DEFAULT_STORAGE_LOCATION_ID,
                             part_size_byte: int = DEFAULT_UPLOAD_PART_SIZE,
                             generate_preview: bool = True,
                             force_restart: bool = False
                             ) -> dict:
    """
    Starts or checks the multipart upload status.
    See: https://docs.synapse.org/rest/POST/file/multipart.html

    :param client: a SynapseBaseClient
    :param file_name: the name of the to-be-uploaded file
    :param content_type: the content type of the to-be-uploaded file
    :param file_size_byte: the size of the to-be-uploaded file in bytes
    :param md5: the md5 of the to-be-uploaded file
    :param storage_location_id: the identifier of the storage location where the file should be uploaded
    :param part_size_byte: the size of one part in bytes
    :param generate_preview: Set to False to indicate that no preview should be generated for this file. Default True.
    :param force_restart: Set to True to clear all upload state for the given file. Default False.
    :return: a dictionary that represents the MultipartUploadStatus object
    """
    validate_type(str, file_name, "file_name")
    validate_type(str, content_type, "content_type")
    validate_type(int, file_size_byte, "file_size_byte")
    validate_type(_hashlib.HASH, md5, "md5")

    upload_request = {
        'contentMD5Hex': md5,
        'contentType': content_type,
        'fileSizeBytes': file_size_byte,
        'partSizeBytes': part_size_byte,
        'fileName': file_name,
        'storageLocationId': storage_location_id,
        'generatePreview': generate_preview
    }
    uri = '/file/multipart'
    if force_restart:
        uri += '?forceRestart=True'

    return client.post(uri,
                       request_body=json.dumps(upload_request),
                       endpoint=client.default_file_endpoint)


def _get_batch_pre_signed_url(client,
                              upload_id: int,
                              content_type: str,
                              parts: typing.List[int]
                              ) -> list:
    """
    Get a batch of pre-signed URLs for the given parts.
    See: https://docs.synapse.org/rest/POST/file/multipart/uploadId/presigned/url/batch.html

    :param upload_id: the identifier for the upload
    :param content_type: the content type of the to-be-uploaded file
    :param parts: a list of part numbers to get pre-signed URLs for
    :return: a list of part pre-signed URLs
    """
    validate_type(int, upload_id, "upload_id")
    validate_type(str, content_type, "content_type")

    if len(parts) == 0:
        return []

    pre_signed_url_request = {'uploadId': upload_id,
                              'partNumbers': parts}
    uri = '/file/multipart/{uploadId}/presigned/url/batch'.format(uploadId=upload_id)
    pre_signed_url_batch = client.post(uri,
                                       request_body=json.dumps(pre_signed_url_request),
                                       endpoint=client.default_file_endpoint)
    for part in pre_signed_url_batch['partPresignedUrls']:
        yield part


def _upload_part(part_pre_signed_url: str,
                 part_data_byte: bytes):
    """
    Uploads a single part to the given pre-signed URL

    :param part_pre_signed_url: the pre-signed URL for the part
    :param part_data_byte: the data to upload in bytes
    """
    validate_type(str, part_pre_signed_url, "part_pre_signed_url")
    validate_type(bytes, part_data_byte, "part_data_byte")

    response = requests.put(part_pre_signed_url, data=part_data_byte)

    # closes response stream
    # see: http://docs.python-requests.org/en/latest/user/advanced/#keep-alive
    if response is not None:
        _ = response.content


def _add_part(client,
              upload_id: int,
              part_number: int,
              part_md5: _hashlib.HASH) -> dict:
    """
    Adds a uploaded part to the multipart upload progress.
    See: https://docs.synapse.org/rest/PUT/file/multipart/uploadId/add/partNumber.html

    :param client: a SynapseBaseClient
    :param upload_id: the identifier for the upload
    :param part_number: the part number to add
    :param part_md5: the md5 of the uploaded part
    :return: a dictionary that represents the AddPartResponse object
    """
    validate_type(int, upload_id, "upload_id")
    validate_type(int, part_number, "part_number")
    validate_type(_hashlib.HASH, part_md5, "part_md5")

    uri = '/file/multipart/{upload_id}/add/{part_number}?partMD5Hex={part_md5}'.format(**{'upload_id': upload_id,
                                                                                          'part_number': part_number,
                                                                                          'part_md5': part_md5})
    return client.put(uri, endpoint=client.default_file_endpoint)


def _complete_multipart_upload(client,
                               upload_id: int) -> dict:
    """
    Completes multipart upload.
    See: https://docs.synapse.org/rest/PUT/file/multipart/uploadId/complete.html

    :param client: a SynapseBaseClient
    :param upload_id: the identifier for the upload
    :return: a dictionary that represents the MultipartUploadStatus object
    """
    validate_type(int, upload_id, "upload_id")

    uri = '/file/multipart/{upload_id}/complete'.format(**{'upload_id': upload_id})
    return client.put(uri, endpoint=client.default_file_endpoint)
