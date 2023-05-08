from abc import ABC, abstractmethod, abstractproperty

class AbstractFile(ABC):
    """
    Represent a records file.
    """
    def __init__(self):
        pass
    
    @abstractproperty
    def key(self):
        pass
    
    @abstractproperty
    def uuid(self):
        pass
    
    @abstractproperty
    def content_type(self):
        pass
    
    @abstractproperty
    def modified(self):
        pass
    
    @abstractmethod
    def get_reader(self):
        pass
    