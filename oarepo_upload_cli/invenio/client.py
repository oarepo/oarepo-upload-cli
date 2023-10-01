from abc import abstractmethod
from typing import Any, Dict, Optional, Union

from oarepo_upload_cli.repository import RepositoryClient, RepositoryRecord
from oarepo_upload_cli.source import SourceRecord
from oarepo_upload_cli.invenio.connection import InvenioConnection
from oarepo_upload_cli.invenio.record import InvenioRepositoryRecord
from oarepo_upload_cli.utils import parse_modified


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
            if len(hits) > 1:
                raise AttributeError(
                    f"Repository returned more than one record for id {record.record_id} with query {params}"
                )
            return self._parse_record(hits[0])

    def create_record(self, record: SourceRecord) -> RepositoryRecord:
        res = self.connection.post(
            url=self._config.collection_url, json=record.metadata
        ).json()
        return self._parse_record(res)

    def _parse_record(self, res):
        return self.record_class(
            record_id=res["id"],
            datetime_modified=parse_modified(
                res, self._config.record_modified_field_name
            ),
            config=self._config,
            connection=self.connection,
            metadata=res,
        )

    def delete_record(self, record: RepositoryRecord):
        record: InvenioRepositoryRecord  # can delete only my record
        self.connection.delete(url=record.self_url)

    def _get_aggregation(self, *path: str) -> Union[Any, None]:
        """
        Sends a request to the given repository URL. Tries to acquire the data from the response determined by the given path.

        Returns the data or prints an error with the description what happened.
        """

        content = self.connection.get(self._config.collection_url).json()

        content_element = content
        for path_element in ["aggregations"] + list(path):
            if path_element not in content_element:
                raise KeyError(
                    f"Path element {path_element} from {path} not found in data {content}"
                )
            content_element = content_element[path_element]
        return content_element
