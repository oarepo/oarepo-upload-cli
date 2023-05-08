from abc import ABC, abstractproperty

class AbstractMetadata(ABC):
    def __init__(self):
        pass
    
    @abstractproperty
    def modified(self):
        """
        Returns the date of the last modification.
        """
        
    @abstractproperty
    def uuid(self):
        """
        Returns the UUID.
        """
    
    