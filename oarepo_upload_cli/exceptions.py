from enum import StrEnum

class EntryPointNotFoundException(Exception):
    """
    Raise when an entry point is not defined.
    """
    pass

class RepositoryCommunicationException(Exception):
    """
    Raised when there is a problem with requesting data from repository happens.
    """    
    pass

class ExceptionMessage(StrEnum):
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