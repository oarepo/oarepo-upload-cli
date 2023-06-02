from abc import ABC, abstractmethod

class AbstractFile(ABC):
    """
    Represent a records file.
    """
    def __init__(self, key):
        self._key = key
    
    @property
    @abstractmethod
    def content_type(self):
        pass
    
    @property
    def key(self):
        return self._key
    
    @property
    @abstractmethod
    def modified(self):
        pass
    
    @property
    @abstractmethod
    def metadata(self):
        pass
    
    @abstractmethod
    def get_reader(self):
        pass