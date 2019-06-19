import pytest
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


def test_anonymous_connection_post():
    anonymous_connect = get_anonymous_connection()
    _, auth, _ = get_test_endpoints()
    username, password = get_test_credentials()
    login_request = {'username': username,
                     'password': password}
    response = anonymous_connect.post("/login", endpoint=auth, request_body=login_request)
    assert response['sessionToken'] is not None


def test_anonymous_connection_put():
    anonymous_connect = get_anonymous_connection()
    _, auth, _ = get_test_endpoints()
    with pytest.raises(SynapseUnauthorizedError):
        anonymous_connect.put("/session", request_body={'sessionToken': 'fake'}, endpoint=auth)


def test_anonymous_connection_delete():
    anonymous_connect = get_anonymous_connection()
    _, auth, _ = get_test_endpoints()
    with pytest.raises(SynapseBadRequestError):
        anonymous_connect.delete("/session", endpoint=auth)


def test_user_connection_get():
    synapse_connection = get_test_user_connection()
    profile = synapse_connection.get("/userProfile")
    assert profile['userName'] == 'test'


def test_user_connection_post():
    synapse_connection = get_test_user_connection()
    project = {
        'name': 'test_'+time.strftime("%Y-%m-%dT%H-%M-%S.000Z", time.gmtime()),
        'concreteType': 'org.sagebionetworks.repo.model.Project'
    }
    created = synapse_connection.post("/entity", request_body=project)
    assert created['id'] is not None


def test_user_connection_put():
    synapse_connection = get_test_user_connection()
    response = synapse_connection.put("/notificationEmail", request_body={'email': 'test@sagebase.org'})
    assert response == ''


def test_user_connection_delete():
    synapse_connection = get_test_user_connection()
    _, _, file = get_test_endpoints()
    response = synapse_connection.delete("/download/list", endpoint=file)
    assert response == ''
