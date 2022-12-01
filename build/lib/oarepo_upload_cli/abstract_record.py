import abc

class AbstractRecord(metaclass=abc.ABCMeta):
    """
    Interface for concrete record.
    """
    @abc.abstractmethod
    def get_metadata(self):
        """
        Returns metadada serializable to JSON in the format that is acceptable by the repository.
        """