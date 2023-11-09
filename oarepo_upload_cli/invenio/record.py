import dataclasses
import json
from functools import cached_property
from typing import Dict
from urllib.parse import urljoin

from oarepo_upload_cli.audit import Audit
from oarepo_upload_cli.config import Config
from oarepo_upload_cli.invenio.connection import InvenioConnection
from oarepo_upload_cli.repository import RepositoryFile, RepositoryRecord, FileStatus
from oarepo_upload_cli.source import SourceRecordFile
from oarepo_upload_cli.utils import JsonType, parse_modified


@dataclasses.dataclass
class InvenioRepositoryRecord(RepositoryRecord):
    config: Config
    connection: InvenioConnection
    metadata: Dict[str, JsonType]
    audit: Audit
    dry_run: bool

    @cached_property
    def files(self) -> Dict[str, RepositoryFile]:
        return {
            file_metadata["key"]: RepositoryFile(
                key=file_metadata["key"],
                datetime_modified=parse_modified(
                    file_metadata, self.config.file_modified_field_name
                ),
                file_status=file_metadata["status"],
                metadata=file_metadata,
            )
            for file_metadata in self.connection.get(self.link_url("files")).json()[
                "entries"
            ]
        }

    def link_url(self, key):
        base_url = self.config.collection_url
        if not base_url.endswith("/"):
            base_url += "/"
        return urljoin(base_url, self.metadata["links"][key])

    @property
    def self_url(self):
        return self.link_url("self")

    @property
    def files_url(self):
        return self.link_url("files")

    def update_metadata(self, new_metadata: Dict[str, JsonType]):
        self.audit.info(f"Updating metadata of record {self.record_id}")
        self.audit.debug(
            f"New metadata: {json.dumps(new_metadata, ensure_ascii=False)}"
        )
        if self.dry_run:
            return
        self.metadata = self.connection.put(url=self.self_url, json=new_metadata).json()

    def create_file(self, file: SourceRecordFile) -> RepositoryFile:
        self.audit.info(f"Creating file {file.key} of record {self.record_id}")
        self.audit.debug(
            f"File metadata: {json.dumps(file.metadata, ensure_ascii=False)}"
        )
        if self.dry_run:
            return RepositoryFile(
                key=file.key,
                datetime_modified=file.datetime_modified,
                file_status=FileStatus.COMPLETED,
                metadata=file.metadata,
            )
        # raises exception on error
        self.audit.debug("Initiating file upload for {file.key}")
        self.connection.post(url=self.files_url, json=[{"key": file.key}])
        url = f"{self.files_url}/{file.key}"
        content_url = f"{self.files_url}/{file.key}/content"
        commit_url = f"{self.files_url}/{file.key}/commit"

        # put metadata
        self.audit.debug("Putting file metadata for {file.key}")
        self.connection.put(url=url, json=file.metadata)

        # upload data
        self.audit.debug("Uploading data for {file.key}")
        self.connection.put(
            url=content_url,
            headers={"Content-Type": file.content_type},
            data=file.reader(),
        )

        # commit
        self.audit.debug("Committing file {file.key}")
        self.connection.post(commit_url)

        # reread the metadata to make sure they have been uploaded
        self.audit.debug("Fetching stored metadata for {file.key}")
        fetched_metadata = self.connection.get(url).json()
        repository_file = RepositoryFile(
            key=file.key,
            metadata=fetched_metadata,
            datetime_modified=parse_modified(
                fetched_metadata, self.config.file_modified_field_name
            ),
            file_status=fetched_metadata["status"],
        )
        self.files[file.key] = repository_file
        return repository_file

    def update_file(self, file: SourceRecordFile) -> RepositoryFile:
        self.audit.info(f"Updating file {file.key} of record {self.record_id}")
        # invenio can not do file update, so delete and create again
        self.delete_file(file)
        return self.create_file(file)

    def delete_file(self, file: SourceRecordFile):
        self.audit.info(f"Deleting file {file.key} of record {self.record_id}")
        if self.dry_run:
            return

        url = f"{self.files_url}/{file.key}"
        self.connection.delete(url)
        self.files.pop(file.key, None)
