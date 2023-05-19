from abc import ABC, abstractmethod, abstractproperty
from abstract_file import AbstractFile
from abstract_metadata import AbstractMetadata
from typing import List

class AbstractRecord(ABC):
    """
    Describes a concrete record.
    """

    @abstractmethod
    def __init__(self, updated: str, id: str = None):
        self._updated = updated
        self._id = id

    @abstractproperty
    def metadata(self) -> AbstractMetadata:
        """
        Returns a metadata serializable to JSON acceptable by a repository.
        """

    @abstractproperty
    def files(self) -> List[AbstractFile]:
        pass

    @property
    def id(self):
        """
        Returns the record's ID.
        """
        
        return self._id

    @id.setter
    def id(self, value):
        """
        Sets the given value as a new value of the record's ID.
        """
        
        self._id = value