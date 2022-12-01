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