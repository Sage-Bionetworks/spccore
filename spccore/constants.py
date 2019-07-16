import os
import requests
from .__version__ import __version__


# Generic constants

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"
CONTENT_TYPE_HEADER = 'content-type'
JSON_CONTENT_TYPE = 'application/json'


# Synapse specific constants

SYNAPSE_DEFAULT_REPO_ENDPOINT = "https://repo-prod.prod.sagebase.org/repo/v1"
SYNAPSE_DEFAULT_AUTH_ENDPOINT = "https://repo-prod.prod.sagebase.org/auth/v1"
SYNAPSE_DEFAULT_FILE_ENDPOINT = "https://repo-prod.prod.sagebase.org/file/v1"

SYNAPSE_USER_ID_HEADER = 'userId'
SYNAPSE_SIGNATURE_TIMESTAMP_HEADER = 'signatureTimestamp'
SYNAPSE_SIGNATURE_HEADER = 'signature'
SYNAPSE_USER_AGENT_HEADER = {'User-Agent': 'spccore/{version} {default}'.format(
    **{'version': __version__, 'default': requests.utils.default_user_agent()})}

SYNAPSE_DEFAULT_HTTP_HEADERS = {CONTENT_TYPE_HEADER: 'application/json; charset=UTF-8',
                                'Accept': 'application/json; charset=UTF-8'}

SYNAPSE_DEFAULT_STORAGE_LOCATION_ID = 1

SYNAPSE_DEFAULT_CACHE_ROOT_DIR = os.path.join('~', '.synapseCache')
SYNAPSE_DEFAULT_CACHE_MAP_FILE_NAME = ".cacheMap"
SYNAPSE_DEFAULT_CACHE_BUCKET_SIZE = 1000
