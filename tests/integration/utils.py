import configparser
import os
from spccore.connection import *


DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.synapseConfig')
DEFAULT_CONFIG_ENDPOINT_SECTION = "endpoints"
DEFAULT_CONFIG_AUTH_SECTION = "authentication"
DEFAULT_CONFIG_USERNAME_OPT = "username"
DEFAULT_CONFIG_PASSWORD_OPT = "password"
DEFAULT_CONFIG_REPO_ENDPOINT_OPT = "repoEndpoint"


def get_test_endpoint() -> str:
    """
    Retrieve the dev stack endpoint

    :return: the dev stack endpoint
    """
    endpoint, username, api_key = _get_test_info()
    return endpoint


def get_test_user_connection() -> SynapseConnection:
    """
    Get a connection using the credentials found in the config file

    :return: the test user's connection to Synapse
    """
    endpoint, username, api_key = _get_test_info()
    return get_connection(base_endpoint=endpoint, username=username, api_key=api_key)


def _get_config_info() -> (str, str, str):
    """
    Read ~/.synapseConfig and retrieve endpoint, test username and password

    :return: endpoint, username and api_key
    """
    config = configparser.ConfigParser()
    config.read(DEFAULT_CONFIG_PATH)
    return config.get(DEFAULT_CONFIG_ENDPOINT_SECTION, DEFAULT_CONFIG_REPO_ENDPOINT_OPT), \
           config.get(DEFAULT_CONFIG_AUTH_SECTION, DEFAULT_CONFIG_USERNAME_OPT), \
           config.get(DEFAULT_CONFIG_AUTH_SECTION, DEFAULT_CONFIG_PASSWORD_OPT)


def _get_api_key(endpoint: str, username: str, password: str) -> str:
    """
    Retrieve test user API key

    :param endpoint: the Synapse server endpoint
    :param username: the Synapse username
    :param password: the Synapse user's password
    :return: the Synapse user's API key
    """
    anonymous_connection = get_connection(base_endpoint=endpoint)
    request_body = {'email': username, 'password': password}
    session_token = anonymous_connection.post('/session', request_body=request_body)['sessionToken']
    headers = {'sessionToken': session_token, 'Accept': 'application/json'}
    return anonymous_connection.get('/secretKey', headers=headers)['secretKey']


def _get_test_info() -> (str, str, str):
    """
    Retrieve test endpoint, username and api key

    :return: endpoint, username and api_key
    """
    endpoint, username, password = _get_config_info()
    return endpoint, username, _get_api_key(endpoint, username, password)
