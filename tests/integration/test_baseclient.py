import pytest
import time

from spccore.exceptions import *


def test_anonymous_connection_endpoints(anonymous_connection, test_endpoints):
    repo_endpoint, auth_endpoint, file_endpoint = test_endpoints
    assert repo_endpoint == anonymous_connection.default_repo_endpoint
    assert auth_endpoint == anonymous_connection.default_auth_endpoint
    assert file_endpoint == anonymous_connection.default_file_endpoint


def test_user_connection_endpoints(test_user_connection, test_endpoints):
    repo_endpoint, auth_endpoint, file_endpoint = test_endpoints
    assert repo_endpoint == test_user_connection.default_repo_endpoint
    assert auth_endpoint == test_user_connection.default_auth_endpoint
    assert file_endpoint == test_user_connection.default_file_endpoint


def test_anonymous_connection_get(anonymous_connection):
    version = anonymous_connection.get("/version")
    assert version['version'] is not None


def test_anonymous_connection_post(anonymous_connection, test_endpoints, test_credentials):
    _, auth, _ = test_endpoints
    username, password = test_credentials
    login_request = {'username': username,
                     'password': password}
    response = anonymous_connection.post("/login", endpoint=auth, request_body=login_request)
    assert response['sessionToken'] is not None


def test_anonymous_connection_put(anonymous_connection, test_endpoints):
    _, auth, _ = test_endpoints
    # Synapse does not have any PUT methods accessible by anonymous users
    with pytest.raises(SynapseUnauthorizedError):
        anonymous_connection.put("/session", request_body={'sessionToken': 'fake'}, endpoint=auth)


def test_anonymous_connection_delete(anonymous_connection, test_endpoints):
    _, auth, _ = test_endpoints
    with pytest.raises(SynapseBadRequestError):
        anonymous_connection.delete("/session", endpoint=auth)


def test_user_connection_get(test_user_connection):
    profile = test_user_connection.get("/userProfile")
    assert profile['userName'] == 'test'


def test_user_connection_post(test_user_connection):
    project = {
        'name': 'test_'+time.strftime("%Y-%m-%dT%H-%M-%S.000Z", time.gmtime()),
        'concreteType': 'org.sagebionetworks.repo.model.Project'
    }
    created = test_user_connection.post("/entity", request_body=project)
    assert created['id'] is not None


def test_user_connection_put(test_user_connection):
    response = test_user_connection.put("/notificationEmail", request_body={'email': 'test@sagebase.org'})
    assert response == ''


def test_user_connection_delete(test_user_connection, test_endpoints):
    _, _, file = test_endpoints
    response = test_user_connection.delete("/download/list", endpoint=file)
    assert response == ''
