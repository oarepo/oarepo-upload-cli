from datetime import datetime
from typing import Callable, Optional

from oarepo_upload_cli.config import Config
from oarepo_upload_cli.repository import RepositoryClient, RepositoryRecord
from oarepo_upload_cli.source import RecordSource, SourceRecord
from oarepo_upload_cli.utils import noop


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
        callback: Callable[[SourceRecord, int, int, str], None] = noop,
    ):
        """
        :param modified_after:      datetime when to start uploads
        :param modified_before:     datetime when to stop uploads
        :param callback: function(source_record: SourceRecord, current_record_count, approximate_records_count, message)
        :return: number of uploaded/deleted/modified records
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

            def local_callback(msg):
                callback(
                    source_record,
                    record_cnt,
                    approximate_records_count,
                    msg,
                )

            local_callback("checking")

            repository_record = self._create_update_record_metadata(
                source_record,
                local_callback,
            )

            if not repository_record:
                continue

            self._create_update_record_files(
                source_record, repository_record, local_callback
            )

    def _create_update_record_metadata(
        self, source_record, callback
    ) -> Optional[RepositoryRecord]:
        repository_record = self.repository.get_record(source_record)

        if source_record.deleted:
            if repository_record:
                self.repository.delete_record(repository_record)
                callback("deleted")
            return None

        if not repository_record:
            repository_record = self.repository.create_record(source_record)
            callback("created")

        elif repository_record.datetime_modified < source_record.datetime_modified:
            repository_record.update_metadata(source_record.metadata)
            callback("updated")

        return repository_record

    @staticmethod
    def _create_update_record_files(
        source_record: SourceRecord, repository_record: RepositoryRecord, callback
    ):
        processed_keys = set()
        for f in source_record.files:
            existing = repository_record.files.get(f.key)
            if existing:
                if existing.needs_updating(f):
                    repository_record.update_file(f)
                    callback(f"{f.key} uploaded")
            else:
                repository_record.create_file(f)
                callback(f"{f.key} uploaded")
            processed_keys.add(f.key)

        for f in list(repository_record.files.values()):
            if f.key not in processed_keys:
                repository_record.delete_file(f)
                callback(f"{f.key} deleted")
