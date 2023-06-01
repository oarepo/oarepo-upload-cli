from typing import Dict

from oarepo_upload_cli.abstract_repository_records_handler import AbstractRepositoryRecordsHandler


class TestRepositoryRecordsHandler(AbstractRepositoryRecordsHandler):
    def get_id_query(self, id) -> Dict[str, str]:
        return {
            'metadata_systemIdentifiers_identifier': str(id),
            'metadata_systemIdentifiers_scheme': 'catalogueSysNo'
        }