from datetime import datetime
from typing import Callable

from oarepo_upload_cli.base.repository_client import RepositoryClient
from oarepo_upload_cli.base.source import RecordSource, SourceRecord
from oarepo_upload_cli.config import Config


class Uploader:
    def __init__(
        self, config: Config, source: RecordSource, repository: RepositoryClient
    ):
        self.config = config
        self.source = source
        self.repository = repository

    def upload(
        self,
        modified_after: datetime = None,
        modified_before: datetime = None,
        callback: Callable[[SourceRecord, int, int, str], None] = None,
    ):
        """
        :param modified_after:      datetime when to start uploads
        :param modified_before:     datetime when to stop uploads
        :param callback: function(source_record: SourceRecord, current_record_count, approximate_records_count, message)
        :return:
        """
        if not modified_before:
            modified_before = datetime.utcnow()
        if not modified_after:
            modified_after = self.repository.get_last_modification_date()

        approximate_records_count = self.source.get_records_count(
            modified_after, modified_before
        )

        for record_cnt, source_record in enumerate(
            self.source.get_records(modified_after, modified_before)
        ):
            callback(source_record, record_cnt, approximate_records_count, "processing")
            repository_record = self._create_update_record_metadata(source_record)
            if not repository_record:
                callback(
                    source_record, record_cnt, approximate_records_count, "deleted"
                )
                continue
            self._create_update_record_files(source_record, repository_record)
            callback(
                source_record,
                record_cnt,
                approximate_records_count,
                "uploaded",
            )

    def _create_update_record_metadata(self, source_record):
        repository_record = self.repository.get_record(source_record)
        if source_record.deleted:
            if repository_record:
                self.repository.delete_record(repository_record)
            return None
        if not repository_record:
            repository_record = self.repository.create_record(source_record)
        elif repository_record.datetime_modified < source_record.datetime_modified:
            repository_record.update_metadata(source_record.metadata)
        return repository_record

    def _create_update_record_files(self, source_record, repository_record):
        processed_keys = set()
        for f in source_record.files:
            repository_record.create_update_file(f)
            processed_keys.add(f.key)
        for f in list(repository_record.files):
            if f.key not in processed_keys:
                repository_record.delete_file(f)
