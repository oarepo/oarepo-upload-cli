import abc

class AbstractRecord(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, updated: str, id: str = None):
        self._updated = updated
        self._id = id

    """
    Interface for a concrete record.
    """
    @abc.abstractmethod
    def get_metadata(self):
        """
        Returns metadada serializable to JSON in the format that is acceptable by the repository.
        """

    @property
    @abc.abstractmethod
    def id(self):
        """
        """

    @id.setter
    @abc.abstractmethod
    def id(self, value):
        """
        """