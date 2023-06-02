from enum import Enum

class EntryPointNotFoundException(Exception):
    """
    Raise when an entry point is not defined.
    """
    pass

class RepositoryCommunicationException(Exception):
    """
    Raised when there is a problem with requesting data from repository happens.
    """    
    
    def __init__(self, message, error, payload=None, url=None):
        super().__init__(message)
        self._error = error
        self._payload = payload
        
        if url:
            print(f'Exception on a request with url: {url}.')
        
        if payload:
            print(f'Exception\'s payload: {payload}.')

class ExceptionMessage(Enum):
    """
    Collection of string representing exception error messages.
    """
    AbstractSourceNotFound = 'Abstract record source has not been found'
    AbstractRecordNotFound = 'Abstract record has not been found'
    ConnectionError = 'Network problem has occurred'
    EntryPointNotProvided = 'Entry point not provided'
    HTTPError = 'HTTP error has occured'
    JSONContentNotSerializable = 'Response could not be serialized'
    MultipleEntryPoints = 'Multiple entry points present, can not choose one'