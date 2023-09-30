import dataclasses
from datetime import datetime
from functools import cached_property
from typing import Dict
from urllib.parse import urljoin

from oarepo_upload_cli.base.repository import RepositoryFile, RepositoryRecord
from oarepo_upload_cli.base.source import SourceRecordFile
from oarepo_upload_cli.invenio.connection import InvenioConnection
from oarepo_upload_cli.types import JsonType


@dataclasses.dataclass
class InvenioRepositoryFile(RepositoryFile):
    metadata: Dict[str, JsonType]
    file_modified_field_name: str

    @property
    def datetime_modified(self):
        if self.file_modified_field_name in (self.metadata.get("metadata") or {}):
            return datetime.fromisoformat(
                self.metadata["metadata"][self.file_modified_field_name]
            )


@dataclasses.dataclass
class InvenioRepositoryRecord(RepositoryRecord):
    connection: InvenioConnection
    base_url: str
    metadata: Dict[str, JsonType]
    record_modified_field_name: str
    file_modified_field_name: str

    @cached_property
    def files(self) -> Dict[str, InvenioRepositoryFile]:
        return {
            x["key"]: InvenioRepositoryFile(x["key"], x, self.file_modified_field_name)
            for x in self.connection.get(self.link_url("files")).json()["entries"]
        }

    @property
    def record_id(self):
        return self.metadata["id"]

    def link_url(self, key):
        base_url = self.base_url
        if not base_url.endswith("/"):
            base_url += "/"
        return urljoin(base_url, self.metadata["links"][key])

    @property
    def self_url(self):
        return self.link_url("self")

    @property
    def files_url(self):
        return self.link_url("files")

    @property
    def datetime_modified(self):
        return datetime.fromisoformat(
            self.metadata["metadata"][self.record_modified_field_name]
        )

    def update_metadata(self, new_metadata: Dict[str, JsonType]):
        self.metadata = self.connection.put(url=self.self_url, json=new_metadata).json()

    def create_update_file(self, file: SourceRecordFile) -> bool:
        existing_file: RepositoryFile
        if file.key in self.files:
            existing_file = self.files[file.key]
            if (
                existing_file.datetime_modified
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
            data=file.get_reader(),
        )

        # commit
        self.connection.post(commit_url)

        # reread the metadata to make sure they have been uploaded
        repository_file = InvenioRepositoryFile(
            key=file.key,
            metadata=self.connection.get(url),
            file_modified_field_name=self.file_modified_field_name,
        )
        self.files[file.key] = repository_file

    def delete_file(self, file: SourceRecordFile):
        url = f"{self.files_url}/{file.key}"
        self.connection.delete(url)
        self.files.pop(file.key, None)
