from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class RecordFile(ABC):
    """
    Represent a records file.
    """

    def __init__(self, key):
        self._key = key

    @property
    @abstractmethod
    def content_type(self):
        pass

    @property
    def key(self):
        return self._key

    @property
    @abstractmethod
    def datetime_modified(self) -> datetime:
        pass

    @property
    @abstractmethod
    def metadata(self):
        pass

    @abstractmethod
    def get_reader(self):
        pass


class FileStatus(str, Enum):
    """
    Based on: https://github.com/inveniosoftware/invenio-records-resources/blob/5335294dade21decea0f527022d96e12e1ffad52/invenio_records_resources/services/files/schema.py#L115
    """

    COMPLETED = "completed"
    PENDING = "pending"
