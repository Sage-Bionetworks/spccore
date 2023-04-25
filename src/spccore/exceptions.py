"""Synapse client Exceptions"""
from typing import Optional

import requests  # type: ignore


class SynapseClientError(Exception):
    """Exception thrown by the client"""

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None):
        """Base Client Error class

        Args:
            message (str): The reason why this error is raised. Defaults to None.
            error_code (str): The error code from Synapse backend. Defaults to None.
        """
        super().__init__(message)
        self.error_code = error_code


class SynapseBadRequestError(SynapseClientError):
    """Synapse Bad Request Error"""


class SynapseUnauthorizedError(SynapseClientError):
    """Synapse Unauthorized Error"""


class SynapseNotFoundError(SynapseClientError):
    """Synapse Not Found Error"""


class SynapseConflictError(SynapseClientError):
    """Synapse Conflict Error"""


class SynapseDeprecatedError(SynapseClientError):
    """Synapse Deprecated Error"""


class SynapsePreconditionFailedError(SynapseClientError):
    """Synapse Precondition Failed Error"""


class SynapseLockedError(SynapseClientError):
    """Synapse Locked Error"""


class SynapseTooManyRequestError(SynapseClientError):
    """Synapse Too Many Request Error"""


class SynapseServerError(SynapseClientError):
    """Synapse Server Error"""


class SynapseTemporarilyUnavailableError(SynapseClientError):
    """Synapse Temporarily Unavailable Error"""


ERRORS = {
    400: SynapseBadRequestError,
    401: SynapseUnauthorizedError,
    403: SynapseUnauthorizedError,
    404: SynapseNotFoundError,
    409: SynapseConflictError,
    410: SynapseDeprecatedError,
    412: SynapsePreconditionFailedError,
    423: SynapseLockedError,
    429: SynapseTooManyRequestError,
    500: SynapseServerError,
    503: SynapseTemporarilyUnavailableError,
}


def check_status_code_and_raise_error(response: requests.Response) -> None:
    """Check status code and raise error if status code is above 400

    Args:
        response (requests.Response): _description_

    Raises:
        SynapseClientError: Synapse client error
    """
    error = None
    if 400 <= response.status_code < 500:
        error = ERRORS.get(response.status_code, SynapseClientError)
    if response.status_code >= 500:
        error = ERRORS.get(response.status_code, SynapseServerError)
    if error is not None:
        reason = response.reason
        if (reason is None or reason == "") and "reason" in response.json():
            reason = response.json()["reason"]
        if "errorCode" in response.json():
            error_code = response.json()["errorCode"]
        else:
            error_code = response.status_code
        raise error(message=reason, error_code=error_code)
