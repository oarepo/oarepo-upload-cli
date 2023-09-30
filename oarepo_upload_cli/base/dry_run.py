import copy
import datetime
import json
from typing import Dict, Optional

from oarepo_upload_cli.base.record_file import RecordFile
from oarepo_upload_cli.base.repository_client import RepositoryClient, RepositoryRecord
from oarepo_upload_cli.base.source import SourceRecord, RecordMetadata


class DryRepositoryRecord(RepositoryRecord):
    def __init__(self, record: SourceRecord):
        self.record = record

    @property
    def datetime_modified(self):
        return self.record.metadata.datetime_modified

    @property
    def record_id(self):
        return self.record.id

    @property
    def files(self):
        return []

    def create_update_file(self, file: RecordFile):
        print(f"Creating or updating file {file.key} of record {self.record_id}")

    def create_file(self, file: RecordFile):
        print(f"Creating file {file.key} of record {self.record_id}")

    def update_file(self, file: RecordFile):
        print(f"Updating file {file.key} of record {self.record_id}")

    def delete_file(self, file: RecordFile):
        print(f"Deleting file {file.key} of record {self.record_id}")

    def update_metadata(self, new_metadata: RecordMetadata):
        print(f"Updating metadata of record {self.record_id}: {new_metadata.metadata}")


class DryRepositoryClient(RepositoryClient):
    def get_id_query(self, source_record_id: str) -> Dict[str, str]:
        return {}

    def get_last_modification_date(self) -> Optional[str]:
        return None

    def get_record(self, source_record: SourceRecord) -> RepositoryRecord:
        return None

    def create_record(self, source_record: SourceRecord) -> RepositoryRecord:
        print(
            f"\nCreating {source_record.id} {json.dumps(source_record.metadata, ensure_ascii=False, indent=4)}"
        )
        return DryRepositoryRecord(source_record.metadata)

    def delete_record(self, record: RepositoryRecord):
        print(f"\nDeleting {record.record_id}")
