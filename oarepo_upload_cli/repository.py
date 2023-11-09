import dataclasses
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from oarepo_upload_cli.audit import Audit
from oarepo_upload_cli.config import Config
from oarepo_upload_cli.source import SourceRecord, SourceRecordFile
from oarepo_upload_cli.utils import JsonType


@dataclasses.dataclass
class RepositoryFile:
    key: str
    datetime_modified: datetime
    file_status: "FileStatus"
    metadata: Dict[str, JsonType]

    def needs_updating(self, source: SourceRecordFile):
        return not (
            self.file_status == FileStatus.COMPLETED
            and self.datetime_modified
            and self.datetime_modified >= source.datetime_modified
        )


@dataclasses.dataclass
class RepositoryRecord(ABC):
    record_id: str
    datetime_modified: datetime
    audit: Audit

    @property
    @abstractmethod
    def files(self) -> Dict[str, RepositoryFile]:
        return {}

    @abstractmethod
    def create_file(self, file: SourceRecordFile):
        pass

    @abstractmethod
    def update_file(self, file: SourceRecordFile):
        pass

    @abstractmethod
    def delete_file(self, file: SourceRecordFile):
        """
        Tries to delete a given file of a given record by its key.
        """

    @abstractmethod
    def update_metadata(self, new_metadata: Dict[str, JsonType]):
        """
        Perform actualization of a given records metadata.
        """


class RepositoryClient(ABC):
    def __init__(self, config: Config, audit: Audit, dry_run):
        self.config = config
        self.audit = audit
        self.dry_run = dry_run

    @abstractmethod
    def get_id_query(self, source_record_id: str) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_last_modification_date(self) -> Optional[str]:
        pass

    def get_record(self, source_record: SourceRecord) -> RepositoryRecord:
        """
        Creates a record in the repository with the given metadata.

        Returns created record metadata.
        """

    def create_record(self, source_record: SourceRecord) -> RepositoryRecord:
        """
        Creates a record in the repository with the given metadata.

        Returns created record metadata.
        """

    def delete_record(self, record: RepositoryRecord):
        """
        Tries to delete a given record.
        """


class FileStatus(str, Enum):
    """
    Based on: https://github.com/inveniosoftware/invenio-records-resources/blob/5335294dade21decea0f527022d96e12e1ffad52/invenio_records_resources/services/files/schema.py#L115
    """

    COMPLETED = "completed"
    PENDING = "pending"
