from abc import ABC, abstractmethod

class AbstractFile(ABC):
    """
    Represent a records file.
    """
    def __init__(self):
        pass
    
    @property
    @abstractmethod
    def content_type(self):
        pass
    
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
    