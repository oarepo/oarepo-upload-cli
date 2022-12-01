from typing import Iterable

from abstract_record_source import AbstractRecordSource
from test_record import TestRecord

class TestSource(AbstractRecordSource):
    def get_records(self, updated_after_timestamp: str) -> Iterable[TestRecord]:
        pass

    def get_records_count(self, updated_after_timestamp: str) -> int:
        pass