from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Optional

from oarepo_upload_cli.base.record_file import RecordFile
from oarepo_upload_cli.base.source import SourceRecord, RecordMetadata
from oarepo_upload_cli.config import Config


class RepositoryFile(ABC):
    @property
    @abstractmethod
    def datetime_modified(self):
        pass

    @property
    @abstractmethod
    def key(self):
        pass


class RepositoryRecord(ABC):
    @property
    @abstractmethod
    def datetime_modified(self):
        pass

    @property
    @abstractmethod
    def record_id(self):
        pass

    @property
    @abstractmethod
    def files(self):
        return []

    @abstractmethod
    def create_update_file(self, file: RecordFile):
        pass

    @abstractmethod
    def create_file(self, file: RecordFile):
        pass

    @abstractmethod
    def update_file(self, file: RecordFile):
        pass

    @abstractmethod
    def delete_file(self, file: RecordFile):
        """
        Tries to delete a given file of a given record by its key.
        """

    @abstractmethod
    def update_metadata(self, new_metadata: RecordMetadata):
        """
        Perform actualization of a given records metadata.
        """


class RepositoryClient(ABC):
    def __init__(self, config: Config):
        self._config = config

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
        pass

    def delete_record(self, record: RepositoryRecord):
        """
        Tries to delete a given record.
        """
