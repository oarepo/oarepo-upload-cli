import abc
from datetime import datetime
from typing import Iterable

from oarepo_upload_cli.abstract_record import AbstractRecord

class AbstractRecordSource(metaclass=abc.ABCMeta):
    """
    Interface for concrete record source that generates records.
    """
    @abc.abstractmethod
    def get_records(self, modified_after: datetime=None, modified_before: datetime=None) -> Iterable[AbstractRecord]:
        """
        Generator returning records of type AbstractRecord limited by given timestamps.
        If no timestamps are provided, returns all records.
        """

    @abc.abstractmethod
    def get_records_count(self, modified_after: datetime=None, modified_before: datetime=None) -> int:
        """
        Approximate size of the collection of records returned.
        """