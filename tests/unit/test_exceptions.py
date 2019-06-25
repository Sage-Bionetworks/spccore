from unittest.mock import patch
from spccore.exceptions import *


def test_check_status_code_and_raise_error_2xx():
    response = requests.Response()
    response.status_code = 200
    check_status_code_and_raise_error(response)


def test_check_status_code_and_raise_error_4xx_with_reason():
    response = requests.Response()
    response.status_code = 400
    response.reason = "some reason"
    json = {}
    with patch.object(requests.Response, "json", return_value=json):
        try:
            check_status_code_and_raise_error(response)
        except SynapseClientError as e:
            assert isinstance(e, SynapseBadRequestError)
            assert e.message == response.reason
            assert e.error_code is None


def test_check_status_code_and_raise_error_4xx_with_json():
    response = requests.Response()
    response.status_code = 401
    response.reason = ""
    reason = 'some reason'
    json = {'reason': reason}
    with patch.object(requests.Response, "json", return_value=json):
        try:
            check_status_code_and_raise_error(response)
        except SynapseClientError as e:
            assert isinstance(e, SynapseUnauthorizedError)
            assert e.message == reason
            assert e.error_code is None


def test_check_status_code_and_raise_error_5xx_with_error_code():
    response = requests.Response()
    response.status_code = 503
    response.reason = ""
    reason = 'some reason'
    error_code = 10
    json = {'reason': reason, 'errorCode': error_code}
    with patch.object(requests.Response, "json", return_value=json):
        try:
            check_status_code_and_raise_error(response)
        except SynapseClientError as e:
            assert isinstance(e, SynapseTemporarilyUnavailableError)
            assert e.message == reason
            assert e.error_code == error_code


def test_check_status_code_and_raise_error_unknown_4xx():
    response = requests.Response()
    response.status_code = 418
    response.reason = ""
    reason = 'some reason'
    error_code = 10
    json = {'reason': reason, 'errorCode': error_code}
    with patch.object(requests.Response, "json", return_value=json):
        try:
            check_status_code_and_raise_error(response)
        except SynapseClientError as e:
            assert isinstance(e, SynapseClientError)
            assert e.message == reason
            assert e.error_code == error_code


def test_check_status_code_and_raise_error_unknown_5xx():
    response = requests.Response()
    response.status_code = 501
    response.reason = ""
    reason = 'some reason'
    error_code = 10
    json = {'reason': reason, 'errorCode': error_code}
    with patch.object(requests.Response, "json", return_value=json):
        try:
            check_status_code_and_raise_error(response)
        except SynapseClientError as e:
            assert isinstance(e, SynapseServerError)
            assert e.message == reason
            assert e.error_code == error_code
