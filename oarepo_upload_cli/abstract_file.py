from abc import ABC, abstractmethod

class AbstractFile(ABC):
    """
    Represent a records file.
    """
    def __init__(self):
        pass
    
    @abstractmethod
    @property
    def content_type(self):
        pass
    
    @abstractmethod
    @property
    def modified(self):
        pass
    
    @abstractmethod
    @property
    def metadata(self):
        pass
    
    @abstractmethod
    def get_reader(self):
        pass
    