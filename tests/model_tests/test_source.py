import datetime
from typing import Iterable

from oarepo_upload_cli.abstract_record_source import AbstractRecordSource
from test_record import TestRecord

class TestSource(AbstractRecordSource):
    # prevent pytest from trying to discover tests in the class
    __test__ = False

    def __init__(self, n_samples: int):
        self.n_samples = n_samples

    def get_records(self, updated_after_timestamp: str) -> Iterable[TestRecord]:
        updated_after = datetime.strptime(updated_after_timestamp, '%Y-%m-%d')

        for i in range(self.n_samples):
            date_after = updated_after + datetime.timedelta(days=i)
            yield TestRecord(date_after.strftime('%Y-%m-%d'))

    def get_records_count(self, updated_after_timestamp: str) -> int:
        return self.n_samples