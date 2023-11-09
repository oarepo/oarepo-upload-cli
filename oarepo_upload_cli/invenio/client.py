import json
from typing import Any, Dict, Optional, Union

from oarepo_upload_cli.audit import Audit
from oarepo_upload_cli.invenio.connection import InvenioConnection
from oarepo_upload_cli.invenio.record import InvenioRepositoryRecord
from oarepo_upload_cli.null_repository import NullRepositoryRecord
from oarepo_upload_cli.repository import RepositoryClient, RepositoryRecord
from oarepo_upload_cli.source import SourceRecord
from oarepo_upload_cli.utils import parse_modified


class InvenioRepositoryClient(RepositoryClient):
    record_class = InvenioRepositoryRecord

    def __init__(self, config, audit: Audit, dry_run):
        super().__init__(config, audit, dry_run)
        self.connection = InvenioConnection(config.auth)

    def get_id_query(self, record_id) -> Dict[str, str]:
        return {
            "q": f"{self.config.repository_id_query_field}:{record_id}",
        }

    def get_last_modification_date(self) -> Optional[str]:
        self.audit.trace("Getting last modification date from repository")
        if self.config.repository_last_modification_date_agg:
            agg = self.config.repository_last_modification_date_agg.split(".")
            last_modification_date = self._get_aggregation(*agg)
            self.audit.debug(
                f"Last modification date from repository is {last_modification_date}"
            )
            return last_modification_date
        else:
            return None

    def get_record(self, record: SourceRecord) -> RepositoryRecord:
        self.audit.trace(f"Getting record from repository with id {record.record_id}")
        params = self.get_id_query(record.record_id)

        res = self.connection.get(url=self.config.collection_url, params=params)

        res_payload = res.json()
        hits = res_payload["hits"]["hits"]

        if hits:
            if len(hits) > 1:
                raise AttributeError(
                    f"Repository returned more than one record for id {record.record_id} with query {params}"
                )
            self.audit.debug(
                f"Found record {record.record_id} in repository, id is {hits[0]['id']}"
            )
            repository_record = self._parse_record(hits[0])
            self.audit.trace(
                f"Repository record found, timestamp: {repository_record.datetime_modified}"
            )
            return repository_record
        else:
            self.audit.debug(f"Record {record.record_id} not found in repository")

    def create_record(self, record: SourceRecord) -> RepositoryRecord:
        self.audit.info(
            f"Creating record {record.record_id} in repository, timestamp {record.datetime_modified}"
        )
        self.audit.debug(f"Record metadata: {json.dumps(record.metadata)}")
        if self.dry_run:
            return NullRepositoryRecord(record, self.audit)

        res = self.connection.post(
            url=self.config.collection_url, json=record.metadata
        ).json()
        self.audit.info(
            f"Created record {record.record_id} in repository, id is {res['id']}"
        )
        return self._parse_record(res)

    def _parse_record(self, res):
        return self.record_class(
            record_id=res["id"],
            datetime_modified=parse_modified(
                res, self.config.record_modified_field_name
            ),
            config=self.config,
            connection=self.connection,
            metadata=res,
            audit=self.audit,
            dry_run=self.dry_run,
        )

    def delete_record(self, record: RepositoryRecord):
        self.audit.info(f"Deleting record {record.record_id} from repository")
        if self.dry_run:
            return
        record: InvenioRepositoryRecord  # can delete only my record
        self.connection.delete(url=record.self_url)

    def _get_aggregation(self, *path: str) -> Union[Any, None]:
        """
        Sends a request to the given repository URL. Tries to acquire the data from the response determined by the given path.

        Returns the data or prints an error with the description what happened.
        """

        content = self.connection.get(self.config.collection_url).json()

        content_element = content
        for path_element in ["aggregations"] + list(path):
            if path_element not in content_element:
                raise KeyError(
                    f"Path element {path_element} from {path} not found in data {content}"
                )
            content_element = content_element[path_element]
        return content_element
