from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable

from oarepo_upload_cli.abstract_record import AbstractRecord

class AbstractRecordSource(ABC):
    """
    Describes a source that is used to generate records.
    """
    
    @abstractmethod
    def get_records(self, modified_after: datetime=None, modified_before: datetime=None) -> Iterable[AbstractRecord]:
        """
        Provides a generator that returns records within given timestamps.
        If no timestamps are given, returns all records.
        """

    @abstractmethod
    def get_records_count(self, modified_after: datetime=None, modified_before: datetime=None) -> int:
        """
        Approximates the size of a collection of records being returned.
        """