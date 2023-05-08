from abc import ABC, abstractmethod

class AbstractRecord(ABC):
    """
    Describes a concrete record.
    """

    @abstractmethod
    def __init__(self, updated: str, id: str = None):
        self._updated = updated
        self._id = id

    @abstractmethod
    def get_metadata(self):
        """
        Returns a metadata serializable to JSON acceptable by a repository.
        """

    @property
    @abstractmethod
    def id(self):
        """
        Returns the record's ID.
        """
        
        return self._id

    @id.setter
    @abstractmethod
    def id(self, value):
        """
        Sets the given value as a new value of the record's ID.
        """