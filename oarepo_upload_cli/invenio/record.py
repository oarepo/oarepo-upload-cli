from abc import abstractmethod
from datetime import datetime
from urllib.parse import urljoin

from oarepo_upload_cli.base.record_file import RecordFile
from oarepo_upload_cli.base.repository_client import RepositoryRecord, RepositoryFile
from oarepo_upload_cli.base.source import RecordMetadata
from oarepo_upload_cli.invenio.connection import InvenioConnection


class InvenioRepositoryFile(RepositoryFile):
    def __init__(self, metadata, file_modified_field_name):
        self.metadata = metadata
        self.file_modified_field_name = file_modified_field_name

    @property
    def datetime_modified(self):
        if self.file_modified_field_name in (self.metadata.get("metadata") or {}):
            return datetime.fromisoformat(
                self.metadata["metadata"][self.file_modified_field_name]
            )

    @property
    def key(self):
        return self.metadata["key"]


class InvenioRepositoryRecord(RepositoryRecord):
    def __init__(
        self,
        connection: InvenioConnection,
        base_url,
        metadata,
        record_modified_field_name,
        file_modified_field_name,
    ):
        self.connection = connection
        self.base_url = base_url
        self.metadata = metadata
        self._files = [
            InvenioRepositoryFile(x, file_modified_field_name)
            for x in connection.get(self.link_url("files")).json()["entries"]
        ]
        self.record_modified_field_name = record_modified_field_name

    @property
    def files(self):
        return self._files

    @property
    def record_id(self):
        return self.metadata["id"]

    def link_url(self, key):
        return urljoin(self.base_url, self.metadata["links"][key])

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

    def update_metadata(self, new_metadata: RecordMetadata):
        self.metadata = self.connection.put(
            url=self.self_url, json=new_metadata.metadata
        ).json()

    def create_update_file(self, file: RecordFile):
        existing_file: RepositoryFile
        for existing_file in self.files:
            if existing_file.key == file.key:
                if (
                    not existing_file.datetime_modified
                    or existing_file.datetime_modified < file.datetime_modified
                ):
                    self.delete_file(file)
                    return self.create_file(file)
                break
        else:
            return self.create_file(file)

    def create_file(self, file: RecordFile):
        # raises exception on error
        self.connection.post(url=self.files_url, json=[{"key": file.metadata["key"]}])
        self.update_file(file)

    def update_file(self, file: RecordFile):
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

    def delete_file(self, file: RecordFile):
        url = f"{self.files_url}/{file.key}"
        self.connection.delete(url)
