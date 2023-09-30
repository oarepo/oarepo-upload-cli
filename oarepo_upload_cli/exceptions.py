from enum import Enum


class ExceptionMessage(str, Enum):
    """
    Collection of string representing exception error messages.
    """

    ConnectionError = "Network problem has occurred"
    EntryPointNotProvided = "Entry point not provided"
    HTTPError = "HTTP error has occured"
    JSONContentNotSerializable = "Response could not be serialized"
    MultipleEntryPoints = "Multiple entry points present, can not choose one"


class EntryPointNotFoundException(Exception):
    """
    Raise when an entry point is not defined.
    """

    def __init__(self):
        super().__init__(ExceptionMessage.EntryPointNotProvided.value)


class RepositoryCommunicationException(Exception):
    """
    Raised when there is a problem with requesting data from repository happens.
    """

    def __init__(self, message, error, payload=None, url=None):
        super().__init__(message)
        self._error = error
        self._payload = payload

        if url:
            print(f"Exception on a request with url: {url}.")

        if payload:
            print(f"Exception's payload: {payload}.")
