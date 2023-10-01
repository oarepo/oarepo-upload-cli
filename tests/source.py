from datetime import datetime
from io import BytesIO
from typing import Iterable

from oarepo_upload_cli.source import RecordSource, SourceRecord, SourceRecordFile


def sample_reader():
    return BytesIO("sample.txt".encode("utf-8"))


def new_reader():
    return BytesIO("new.txt".encode("utf-8"))


class TestSource(RecordSource):
    records = {
        datetime(year=2023, month=1, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=1, day=1),
                deleted=False,
                metadata={
                    "metadata": {
                        "title": "Record 1",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=1, day=1).isoformat(),
                    }
                },
                files=[],
            ),
        ],
        datetime(year=2023, month=2, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=1, day=1),
                deleted=False,
                metadata={
                    "metadata": {
                        "title": "Record 1",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=1, day=1).isoformat(),
                    }
                },
                files=[],
            )
        ],
        datetime(year=2023, month=3, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=3, day=1),
                deleted=False,
                metadata={
                    "metadata": {
                        "title": "Record 1 updated in month 3",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=3, day=1).isoformat(),
                    }
                },
                files=[],
            )
        ],
        datetime(year=2023, month=4, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=3, day=1),
                deleted=False,
                metadata={
                    "metadata": {
                        "title": "Record 1 updated in month 3",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=3, day=1).isoformat(),
                    }
                },
                files=[
                    SourceRecordFile(
                        key="sample.txt",
                        content_type="application/octet-stream",
                        datetime_modified=datetime(year=2023, month=4, day=1),
                        metadata={
                            "dateModified": datetime(
                                year=2023, month=4, day=1
                            ).isoformat()
                        },
                        reader=sample_reader,
                    )
                ],
            )
        ],
        datetime(year=2023, month=5, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=5, day=1),
                deleted=False,
                metadata={
                    "metadata": {
                        "title": "Record 1 updated in month 5",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=5, day=1).isoformat(),
                    }
                },
                files=[
                    SourceRecordFile(
                        key="sample.txt",
                        content_type="application/octet-stream",
                        datetime_modified=datetime(year=2023, month=4, day=1),
                        metadata={
                            "dateModified": datetime(
                                year=2023, month=4, day=1
                            ).isoformat()
                        },
                        reader=sample_reader,
                    )
                ],
            )
        ],
        datetime(year=2023, month=6, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=5, day=1),
                deleted=False,
                metadata={
                    "metadata": {
                        "title": "Record 1 updated in month 5",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=5, day=1).isoformat(),
                    }
                },
                files=[
                    SourceRecordFile(
                        key="sample.txt",
                        content_type="application/octet-stream",
                        datetime_modified=datetime(year=2023, month=4, day=1),
                        metadata={
                            "dateModified": datetime(
                                year=2023, month=4, day=1
                            ).isoformat()
                        },
                        reader=sample_reader,
                    ),
                    SourceRecordFile(
                        key="new.txt",
                        content_type="application/octet-stream",
                        datetime_modified=datetime(year=2023, month=6, day=1),
                        metadata={
                            "dateModified": datetime(
                                year=2023, month=6, day=1
                            ).isoformat()
                        },
                        reader=new_reader,
                    ),
                ],
            )
        ],
        datetime(year=2023, month=7, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=5, day=1),
                deleted=False,
                metadata={
                    "metadata": {
                        "title": "Record 1 updated in month 5",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=5, day=1).isoformat(),
                    }
                },
                files=[
                    SourceRecordFile(
                        key="new.txt",
                        content_type="application/octet-stream",
                        datetime_modified=datetime(year=2023, month=6, day=1),
                        metadata={
                            "dateModified": datetime(
                                year=2023, month=6, day=1
                            ).isoformat()
                        },
                        reader=new_reader,
                    ),
                ],
            )
        ],
        datetime(year=2023, month=8, day=1): [
            SourceRecord(
                record_id="1",
                datetime_modified=datetime(year=2023, month=8, day=1),
                deleted=True,
                metadata={
                    "metadata": {
                        "title": "Record 1 updated in month 5",
                        "originalId": "1",
                        "dateModified": datetime(year=2023, month=5, day=1).isoformat(),
                    }
                },
                files=[
                    SourceRecordFile(
                        key="new.txt",
                        content_type="application/octet-stream",
                        datetime_modified=datetime(year=2023, month=6, day=1),
                        metadata={
                            "dateModified": datetime(
                                year=2023, month=6, day=1
                            ).isoformat()
                        },
                        reader=new_reader,
                    ),
                ],
            )
        ],
    }

    def get_records(
        self, modified_after: datetime = None, modified_before: datetime = None
    ) -> Iterable[SourceRecord]:
        for rec_key, rec_vals in self.records.items():
            if modified_after <= rec_key <= modified_before:
                yield from rec_vals

    def get_records_count(
        self, modified_after: datetime = None, modified_before: datetime = None
    ) -> int:
        return len(list(self.get_records(modified_after, modified_before)))
