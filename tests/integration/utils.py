import configparser
import os
from spccore.connection import *


DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.synapseConfig')
DEFAULT_CONFIG_ENDPOINT_SECTION = "endpoints"
DEFAULT_CONFIG_AUTH_SECTION = "authentication"
DEFAULT_CONFIG_USERNAME_OPT = "username"
DEFAULT_CONFIG_PASSWORD_OPT = "password"
DEFAULT_CONFIG_REPO_ENDPOINT_OPT = "repoEndpoint"
DEFAULT_CONFIG_AUTH_ENDPOINT_OPT = "authEndpoint"
DEFAULT_CONFIG_FILE_ENDPOINT_OPT = "fileHandleEndpoint"


def get_anonymous_connection() -> SynapseConnection:
    """
    Retrieve the dev stack endpoint

    :return: the dev stack endpoint
    """
    repo, auth, file = _get_test_endpoints()
    return get_connection(repo_endpoint=repo, auth_endpoint=auth, file_endpoint=file)


def get_test_user_connection() -> SynapseConnection:
    """
    Get a connection using the credentials found in the config file

    :return: the test user's connection to Synapse
    """
    repo, auth, file = _get_test_endpoints()
    username, password = _get_test_credentials()
    api_key = _get_api_key(auth, username, password)
    return get_connection(repo_endpoint=repo,
                          auth_endpoint=auth,
                          file_endpoint=file,
                          username=username,
                          api_key=api_key)


def _get_test_endpoints() -> (str, str, str):
    """
    Read ~/.synapseConfig and retrieve endpoint, test username and password

    :return: repo, auth, and file endpoints
    """
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)
    return config.get(DEFAULT_CONFIG_ENDPOINT_SECTION, DEFAULT_CONFIG_REPO_ENDPOINT_OPT), \
           config.get(DEFAULT_CONFIG_ENDPOINT_SECTION, DEFAULT_CONFIG_AUTH_ENDPOINT_OPT), \
           config.get(DEFAULT_CONFIG_ENDPOINT_SECTION, DEFAULT_CONFIG_FILE_ENDPOINT_OPT)


def _get_test_credentials() -> (str, str):
    """
    Read ~/.synapseConfig and retrieve test username and password

    :return: endpoint, username and api_key
    """
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)
    return config.get(DEFAULT_CONFIG_AUTH_SECTION, DEFAULT_CONFIG_USERNAME_OPT), \
           config.get(DEFAULT_CONFIG_AUTH_SECTION, DEFAULT_CONFIG_PASSWORD_OPT)


def _get_api_key(auth_endpoint: str, username: str, password: str) -> str:
    """
    Retrieve test user API key

    :param repo_endpoint: the Synapse server repository endpoint
    :param auth_endpoint: the Synapse server authentication endpoint
    :param username: the Synapse username
    :param password: the Synapse user's password
    :return: the Synapse user's API key
    """
    anonymous_connection = get_connection()
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
