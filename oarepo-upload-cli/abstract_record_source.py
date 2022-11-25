import abc

from abstract_record import AbstractRecord

class AbstractRecordSource(metaclass=abc.ABCMeta):
    """
    Interface for concrete record provider.
    """
    @abc.abstractmethod
    def get_records(self, updated_after_timestamp: str) -> list[AbstractRecord]:
        """
        Generator returning record of type AbstractRecord newer than the given timestamp.
        """
        raise NotImplementedError