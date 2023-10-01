import dataclasses
from functools import cached_property
from typing import Dict
from urllib.parse import urljoin

from oarepo_upload_cli.config import Config
from oarepo_upload_cli.invenio.connection import InvenioConnection
from oarepo_upload_cli.repository import FileStatus, RepositoryFile, RepositoryRecord
from oarepo_upload_cli.source import SourceRecordFile
from oarepo_upload_cli.utils import JsonType, parse_modified


@dataclasses.dataclass
class InvenioRepositoryRecord(RepositoryRecord):
    config: Config
    connection: InvenioConnection
    metadata: Dict[str, JsonType]

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
        self.metadata = self.connection.put(url=self.self_url, json=new_metadata).json()

    def create_update_file(self, file: SourceRecordFile) -> bool:
        existing_file: RepositoryFile
        if file.key in self.files:
            existing_file = self.files[file.key]
            if (
                existing_file.file_status == FileStatus.COMPLETED
                and existing_file.datetime_modified
                and existing_file.datetime_modified >= file.datetime_modified
            ):
                # no need to update
                return False

            # invenio can not perform update, so at first delete and then create
            self.delete_file(file)

        self.create_file(file)
        return True

    def create_file(self, file: SourceRecordFile):
        # raises exception on error
        self.connection.post(url=self.files_url, json=[{"key": file.key}])
        self.update_file(file)

    def update_file(self, file: SourceRecordFile):
        url = f"{self.files_url}/{file.key}"
        content_url = f"{self.files_url}/{file.key}/content"
        commit_url = f"{self.files_url}/{file.key}/commit"

        # put metadata
        self.connection.put(url=url, json=file.metadata)

        # upload data
        self.connection.put(
            url=content_url,
            headers={"Content-Type": file.content_type},
            data=file.reader(),
        )

        # commit
        self.connection.post(commit_url)

        # reread the metadata to make sure they have been uploaded
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

    def delete_file(self, file: SourceRecordFile):
        url = f"{self.files_url}/{file.key}"
        self.connection.delete(url)
        self.files.pop(file.key, None)
