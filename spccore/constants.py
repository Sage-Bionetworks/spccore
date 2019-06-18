import requests
from .__version__ import __version__


# Synapse specific constants

SYNAPSE_DEFAULT_REPO_ENDPOINT = "http://repo-prod.prod.sagebase.org/repo/v1"
SYNAPSE_DEFAULT_AUTH_ENDPOINT = "http://repo-prod.prod.sagebase.org/auth/v1"
SYNAPSE_DEFAULT_FILE_ENDPOINT = "http://repo-prod.prod.sagebase.org/file/v1"

SYNAPSE_USER_ID_HEADER = 'userId'
SYNAPSE_SIGNATURE_TIMESTAMP_HEADER = 'signatureTimestamp'
SYNAPSE_SIGNATURE_HEADER = 'signature'
SYNAPSE_USER_AGENT_HEADER = {'User-Agent': 'spccore/%(version) %{default}'.format(
    **{'version': __version__, 'default': requests.utils.default_user_agent()})}

SYNAPSE_DEFAULT_HTTP_HEADERS = {'content-type': 'application/json; charset=UTF-8',
                                'Accept': 'application/json; charset=UTF-8'}

SYNAPSE_DEFAULT_STORAGE_LOCATION_ID = 1

# Generic constants

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"
CONTENT_TYPE_HEADER = 'content-type'
JSON_CONTENT_TYPE = 'application/json'
