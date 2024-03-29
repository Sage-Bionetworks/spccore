import configparser
import pytest
from spccore.baseclient import *


DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.synapseConfig')
DEFAULT_CONFIG_ENDPOINT_SECTION = "endpoints"
DEFAULT_CONFIG_AUTH_SECTION = "authentication"
DEFAULT_CONFIG_USERNAME_OPT = "username"
DEFAULT_CONFIG_PASSWORD_OPT = "password"
DEFAULT_CONFIG_REPO_ENDPOINT_OPT = "repoEndpoint"
DEFAULT_CONFIG_AUTH_ENDPOINT_OPT = "authEndpoint"
DEFAULT_CONFIG_FILE_ENDPOINT_OPT = "fileHandleEndpoint"

_config = None


@pytest.fixture
def anonymous_connection(test_endpoints) -> SynapseBaseClient:
    """
    Retrieve the dev stack endpoint

    :return: the dev stack endpoint
    """
    repo_endpoint, auth_endpoint, file_endpoint = test_endpoints
    return get_base_client(repo_endpoint=repo_endpoint, auth_endpoint=auth_endpoint, file_endpoint=file_endpoint)


@pytest.fixture
def test_user_connection(test_endpoints, test_credentials) -> SynapseBaseClient:
    """
    Get a connection using the credentials found in the config file

    :return: the test user's connection to Synapse
    """
    repo_endpoint, auth_endpoint, file_endpoint = test_endpoints
    username, password = test_credentials
    api_key = _get_api_key(repo_endpoint, auth_endpoint, file_endpoint, username, password)
    return get_base_client(repo_endpoint=repo_endpoint,
                           auth_endpoint=auth_endpoint,
                           file_endpoint=file_endpoint,
                           username=username,
                           api_key=api_key)


@pytest.fixture
def test_endpoints() -> (str, str, str):
    """
    Read ~/.synapseConfig and retrieve endpoint, test username and password

    :return: repo, auth, and file endpoints
    """
    config = _get_config()
    return config.get(DEFAULT_CONFIG_ENDPOINT_SECTION, DEFAULT_CONFIG_REPO_ENDPOINT_OPT), \
           config.get(DEFAULT_CONFIG_ENDPOINT_SECTION, DEFAULT_CONFIG_AUTH_ENDPOINT_OPT), \
           config.get(DEFAULT_CONFIG_ENDPOINT_SECTION, DEFAULT_CONFIG_FILE_ENDPOINT_OPT)


@pytest.fixture
def test_credentials() -> (str, str):
    """
    Read ~/.synapseConfig and retrieve test username and password

    :return: endpoint, username and api_key
    """
    config = _get_config()
    return config.get(DEFAULT_CONFIG_AUTH_SECTION, DEFAULT_CONFIG_USERNAME_OPT),\
           config.get(DEFAULT_CONFIG_AUTH_SECTION, DEFAULT_CONFIG_PASSWORD_OPT)


def _get_api_key(repo_endpoint:str,
                 auth_endpoint: str,
                 file_endpoint: str,
                 username: str,
                 password: str) -> str:
    """
    Retrieve test user API key

    :param repo_endpoint: the Synapse server repository endpoint
    :param auth_endpoint: the Synapse server authentication endpoint
    :param file_endpoint: the Synapse server file endpoint
    :param username: the Synapse username
    :param password: the Synapse user's password
    :return: the Synapse user's API key
    """
    anonymous_connection = get_base_client(repo_endpoint=repo_endpoint,
                                           auth_endpoint=auth_endpoint,
                                           file_endpoint=file_endpoint)
    request_body = {'email': username, 'password': password}
    session_token = anonymous_connection.post('/session',
                                              endpoint=auth_endpoint,
                                              request_body=request_body
                                              )['sessionToken']
    headers = {'sessionToken': session_token, 'Accept': 'application/json'}
    return anonymous_connection.get('/secretKey',
                                    endpoint=auth_endpoint,
                                    headers=headers
                                    )['secretKey']


def _get_config():
    global _config
    if _config is None:
        _config = configparser.ConfigParser()
        _config.read(DEFAULT_CONFIG_PATH)
    return _config
