from abc import abstractmethod
from json import JSONDecodeError
from typing import Any, Dict, Optional, Union

import requests

from oarepo_upload_cli.base.repository import RepositoryClient, RepositoryRecord
from oarepo_upload_cli.base.source import SourceRecord
from oarepo_upload_cli.exceptions import (
    ExceptionMessage,
    RepositoryCommunicationException,
)
from oarepo_upload_cli.invenio.connection import InvenioConnection
from oarepo_upload_cli.invenio.record import InvenioRepositoryRecord


class InvenioRepositoryClient(RepositoryClient):
    record_class = InvenioRepositoryRecord

    def __init__(self, config):
        super().__init__(config)
        self.connection = InvenioConnection(config.auth)

    @abstractmethod
    def get_id_query(self, source_record_id: str) -> Dict[str, str]:
        raise NotImplementedError("ID query not implemented")

    @abstractmethod
    def get_last_modification_date(self) -> Optional[str]:
        raise NotImplementedError("Last modification date not implemented")

    def get_record(self, record: SourceRecord) -> RepositoryRecord:
        params = self.get_id_query(record.record_id)

        res = self.connection.get(url=self._config.collection_url, params=params)

        res_payload = res.json()
        hits = res_payload["hits"]["hits"]

        if hits:
            return self.record_class(
                self.connection,
                self._config.collection_url,
                hits[0],
                self._config.record_modified_field_name,
                self._config.file_modified_field_name,
            )

    def create_record(self, record: SourceRecord) -> RepositoryRecord:
        res = self.connection.post(
            url=self._config.collection_url, json=record.metadata
        )
        return self.record_class(
            self.connection,
            self._config.collection_url,
            res.json(),
            self._config.record_modified_field_name,
            self._config.file_modified_field_name,
        )

    def delete_record(self, record: RepositoryRecord):
        record: InvenioRepositoryRecord  # can delete only my record
        self.connection.delete(url=record.self_url)

    def _get_aggregation(self, *path: str) -> Union[Any, None]:
        """
        Sends a request to the given repository URL. Tries to acquire the data from the response determined by the given path.

        Returns the data or prints an error with the description what happened.
        """

        try:
            url = self._config.collection_url
            res = self.connection.get(url)
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(
                ExceptionMessage.ConnectionError, conn_err
            ) from conn_err
        except requests.exceptions.HTTPError as http_err:
            raise RepositoryCommunicationException(
                ExceptionMessage.HTTPError, http_err, res.text, url=url
            ) from http_err
        except Exception as err:
            raise RepositoryCommunicationException(str(err), err) from err

        try:
            content = res.json()
        except JSONDecodeError as serialization_err:
            raise RepositoryCommunicationException(
                ExceptionMessage.JSONContentNotSerializable, serialization_err
            ) from serialization_err

        content_element = content
        for path_element in ["aggregations"] + list(path):
            if path_element not in content_element:
                raise KeyError(
                    f"Path element {path_element} from {path} not found in data {content}"
                )
            content_element = content_element[path_element]
        return content_element
