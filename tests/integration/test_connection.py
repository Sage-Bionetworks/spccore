from spccore.connection import *


def test_get_version():
    synapse_connection = get_connection()
    version = synapse_connection.get("/version")
    print(version)