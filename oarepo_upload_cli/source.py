import dataclasses
from abc import ABC, abstractmethod
from datetime import datetime
from typing import BinaryIO, Callable, Iterable, List

from oarepo_upload_cli.audit import Audit
from oarepo_upload_cli.config import Config
from oarepo_upload_cli.utils import JsonType


class RecordSource(ABC):
    """
    Describes a source that is used to generate records.
    """

    def __init__(self, config: Config, audit: Audit) -> None:
        self._config = config
        self._audit = audit

    @abstractmethod
    def get_records(
        self, modified_after: datetime, modified_before: datetime
    ) -> Iterable["SourceRecord"]:
        """
        Provides a generator that returns records within given timestamps.
        If no timestamps are given, returns all records. The timestamps are not timezone
        aware and are in UTC.
        """

    @abstractmethod
    def get_records_count(
        self, modified_after: datetime, modified_before: datetime
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
class SourceRecordFile:
    """
    Represent a source record file.
    """

    key: str
    content_type: str
    datetime_modified: datetime
    metadata: JsonType
    reader: Callable[[], BinaryIO]
    """Factory method for a reader"""
