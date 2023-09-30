from abc import ABC, abstractmethod
from typing import List

from .record_file import RecordFile

from datetime import datetime
from typing import Iterable

from oarepo_upload_cli.config import Config


class RecordMetadata(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def datetime_modified(self):
        """
        Returns the date of the last modification.
        """

    @property
    @abstractmethod
    def metadata(self):
        pass


class SourceRecord(ABC):
    """
    Describes a concrete record.
    """

    @abstractmethod
    def __init__(self, updated: datetime, id: str = None, deleted: bool = False):
        assert isinstance(updated, datetime)

        self._updated = updated
        self._id = id

        self._deleted = deleted

    @property
    @abstractmethod
    def metadata(self) -> RecordMetadata:
        """
        Returns a metadata serializable to JSON acceptable by a repository.
        """

    @property
    @abstractmethod
    def files(self) -> List[RecordFile]:
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

    @property
    def datetime_modified(self):
        return self._updated


class RecordSource(ABC):
    """
    Describes a source that is used to generate records.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    @abstractmethod
    def get_records(
        self, modified_after: datetime = None, modified_before: datetime = None
    ) -> Iterable[SourceRecord]:
        """
        Provides a generator that returns records within given timestamps.
        If no timestamps are given, returns all records. The timestamps are not timezone
        aware and are in UTC.
        """

    @abstractmethod
    def get_records_count(
        self, modified_after: datetime = None, modified_before: datetime = None
    ) -> int:
        """
        Approximates the size of a collection of records being returned.
        The timestamps are not timezone aware and are in UTC.
        """
