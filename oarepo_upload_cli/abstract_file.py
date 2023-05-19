from abc import ABC, abstractmethod

class AbstractFile(ABC):
    """
    Represent a records file.
    """
    def __init__(self, key):
        self._key = key

    @property
    def metadata(self):
        return {
            'key': self._key
        }

    @property
    @abstractmethod
    def content_type(self):
        pass
    
    @property
    @abstractmethod
    def modified(self):
        pass

    @abstractmethod
    def get_reader(self):
        pass
    