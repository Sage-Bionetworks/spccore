from tests.integration.utils import *


def test_anonymous_connection_endpoints():
    anonymous_connect = get_anonymous_connection()
    repo, auth, file = get_test_endpoints()
    assert repo == anonymous_connect.repo_endpoint
    assert auth == anonymous_connect.auth_endpoint
    assert file == anonymous_connect.file_endpoint

def test_user_connection_endpoints():
    synapse_connection = get_test_user_connection()
    repo, auth, file = get_test_endpoints()
    assert repo == synapse_connection.repo_endpoint
    assert auth == synapse_connection.auth_endpoint
    assert file == synapse_connection.file_endpoint

def test_anonymous_connection_get():
    anonymous_connect = get_anonymous_connection()
    version = anonymous_connect.get("/version")
    assert version['version'] is not None


def test_user_connection_get():
    synapse_connection = get_test_user_connection()
    profile = synapse_connection.get("/userProfile")
    assert profile['userName'] == 'test'
