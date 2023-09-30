import dataclasses
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, List

from oarepo_upload_cli.config import Config

from ..types import JsonType


class RecordSource(ABC):
    """
    Describes a source that is used to generate records.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    @abstractmethod
    def get_records(
        self, modified_after: datetime = None, modified_before: datetime = None
    ) -> Iterable["SourceRecord"]:
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


@dataclasses.dataclass
class SourceRecord:
    """
    Describes a source record.
    """

    record_id: str
    datetime_modified: datetime
    deleted: bool
    metadata: JsonType
    files: List["SourceRecordFile"]


@dataclasses.dataclass
class SourceRecordFile(ABC):
    """
    Represent a source record file.
    """

    key: str
    content_type: str
    datetime_modified: datetime
    metadata: JsonType

    @abstractmethod
    def get_reader(self):
        pass
