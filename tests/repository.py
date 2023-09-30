from typing import Dict, Optional

from oarepo_upload_cli.invenio.client import InvenioRepositoryClient


class TestRepositoryClient(InvenioRepositoryClient):
    def get_id_query(self, record_id: str) -> Dict[str, str]:
        return {"metadata_originalId": record_id}

    def get_last_modification_date(self) -> Optional[str]:
        return None
