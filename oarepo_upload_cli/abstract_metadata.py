from abc import ABC, abstractmethod

class AbstractMetadata(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    @property
    def modified(self):
        """
        Returns the date of the last modification.
        """
    
    @abstractmethod
    @property
    def metadata(self):
        pass