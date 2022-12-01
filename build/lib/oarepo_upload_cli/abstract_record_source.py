import abc
from typing import Iterable

from abstract_record import AbstractRecord

class AbstractRecordSource(metaclass=abc.ABCMeta):
    """
    Interface for concrete record source that generates records.
    """
    @abc.abstractmethod
    def get_records(self, updated_after_timestamp: str) -> Iterable[AbstractRecord]:
        """
        Generator returning records of type AbstractRecord newer than the given timestamp.
        """

    @abc.abstractmethod
    def get_records_count(self, updated_after_timestamp: str) -> int:
        """
        Approximate size of the collection of records returned.
        """