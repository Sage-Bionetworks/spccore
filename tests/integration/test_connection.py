from tests.integration.utils import *


def test_anonymous_connection():
    synapse_connection = get_anonymous_connection()
    version = synapse_connection.get("/version")
    assert version['version'] is not None


def test_user_connection():
    synapse_connection = get_test_user_connection()
    profile = synapse_connection.get("/userProfile")
    assert profile['username'] == 'test'
