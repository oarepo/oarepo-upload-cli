from abc import ABC, abstractmethod
from typing import List

from .abstract_file import AbstractFile
from .abstract_metadata import AbstractMetadata

class AbstractRecord(ABC):
    """
    Describes a concrete record.
    """

    @abstractmethod
    def __init__(self, updated: str, id: str = None, deleted: bool = False):
        self._updated = updated
        self._id = id
        
        self._deleted = deleted

    @property
    @abstractmethod
    def metadata(self) -> AbstractMetadata:
        """
        Returns a metadata serializable to JSON acceptable by a repository.
        """

    @property
    @abstractmethod
    def files(self) -> List[AbstractFile]:
        pass

    @property
    def id(self):
        """
        Returns the record's ID.
        """
        
        return self._id

    @property
    def deleted(self):
        """
        Returns an indicator whether the record was deleted or not.
        """
        
        return self._deleted