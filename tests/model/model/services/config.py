from invenio_records_resources.services import RecordLink
from invenio_records_resources.services import (
    RecordServiceConfig as InvenioRecordServiceConfig,
)
from invenio_records_resources.services import pagination_links
from model.records.api import ModelRecord
from model.services.permissions import ModelPermissionPolicy
from model.services.schema import ModelSchema
from model.services.search import ModelSearchOptions


class ModelServiceConfig(InvenioRecordServiceConfig):
    """ModelRecord service config."""

    url_prefix = "/model/"

    permission_policy_cls = ModelPermissionPolicy
    schema = ModelSchema
    search = ModelSearchOptions
    record_cls = ModelRecord

    components = [*InvenioRecordServiceConfig.components]

    model = "model"

    @property
    def links_item(self):
        return {
            "self": RecordLink("{self.url_prefix}{id}"),
        }

    @property
    def links_search(self):
        return pagination_links("{self.url_prefix}{?args*}")
