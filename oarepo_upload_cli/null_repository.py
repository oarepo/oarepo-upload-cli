import json
from typing import Dict, Optional

from oarepo_upload_cli.audit import Audit
from oarepo_upload_cli.repository import RepositoryClient, RepositoryRecord
from oarepo_upload_cli.source import SourceRecord, SourceRecordFile
from oarepo_upload_cli.utils import JsonType


class NullRepositoryRecord(RepositoryRecord):
    def __init__(self, record: SourceRecord, audit: Audit):
        self.audit = audit
        self.record = record

    @property
    def datetime_modified(self):
        return self.record.datetime_modified

    @property
    def record_id(self):
        return self.record.record_id

    @property
    def files(self):
        return {}

    def create_file(self, file: SourceRecordFile):
        self.audit.info(f"Creating file {file.key} of record {self.record_id}")

    def update_file(self, file: SourceRecordFile):
        self.audit.info(f"Updating file {file.key} of record {self.record_id}")

    def delete_file(self, file: SourceRecordFile):
        self.audit.info(f"Deleting file {file.key} of record {self.record_id}")

    def update_metadata(self, new_metadata: Dict[str, JsonType]):
        self.audit.info(f"Updating metadata of record {self.record_id}: {new_metadata}")


class NullRepositoryClient(RepositoryClient):
    def get_id_query(self, source_record_id: str) -> Dict[str, str]:
        return {}

    def get_last_modification_date(self) -> Optional[str]:
        return None

    def get_record(self, source_record: SourceRecord) -> RepositoryRecord:
        return None

    def create_record(self, source_record: SourceRecord) -> RepositoryRecord:
        self.audit.info(
            f"\nCreating {source_record.record_id} {json.dumps(source_record.metadata, ensure_ascii=False, indent=4)}"
        )
        return NullRepositoryRecord(source_record, self.audit)

    def delete_record(self, record: RepositoryRecord):
        self.audit.info(f"\nDeleting {record.record_id}")
