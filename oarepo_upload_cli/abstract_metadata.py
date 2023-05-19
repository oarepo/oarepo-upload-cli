from abc import ABC, abstractmethod

class AbstractMetadata(ABC):
    def __init__(self):
        pass
    
    @property
    @abstractmethod
    def modified(self):
        """
        Returns the date of the last modification.
        """
    
    @property
    @abstractmethod
    def metadata(self):
        pass