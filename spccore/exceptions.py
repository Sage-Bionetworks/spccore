import requests


class SynapseError(Exception):
    """Exception thrown by the client"""


class SynapseBadRequestError(SynapseError):
    """Synapse Bad Request Error"""


class SynapseUnauthorizedError(SynapseError):
    """Synapse Unauthorized Error"""


class SynapseNotFoundError(SynapseError):
    """Synapse Not Found Error"""


class SynapseConflictError(SynapseError):
    """Synapse Conflict Error"""


class SynapseDeprecatedError(SynapseError):
    """Synapse Deprecated Error"""


class SynapsePreconditionFailedError(SynapseError):
    """Synapse Precondition Failed Error"""


class SynapseLockedError(SynapseError):
    """Synapse Locked Error"""


class SynapseTooManyRequestError(SynapseError):
    """Synapse Too Many Request Error"""


class SynapseServerError(SynapseError):
    """Synapse Server Error"""


class SynapseServerError(SynapseError):
    """Synapse Server Error"""


class SynapseTemporarilyUnavailableError(SynapseError):
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
    error = None
    if 400 <= response.status_code < 500:
        error = ERRORS.get(response.status_code, SynapseError)
    if response.status_code >= 500:
        error = ERRORS.get(response.status_code, SynapseServerError)
    if error is not None:
        reason = response.reason
        if reason is None:
            reason = response.json()['reason']
        raise error(reason)
