from invenio_records_resources.services import (
    RecordLink,
    RecordServiceConfig,
    pagination_links,
)
from invenio_records_resources.services.records.components import FilesOptionsComponent
from oarepo_runtime.config.service import PermissionsPresetsConfigMixin
from oarepo_runtime.relations.components import CachingRelationsComponent

from uct_theses.records.api import UctThesesRecord
from uct_theses.services.records.schema import UctThesesSchema
from uct_theses.services.records.search import UctThesesSearchOptions


class UctThesesServiceConfig(PermissionsPresetsConfigMixin, RecordServiceConfig):
    """UctThesesRecord service config."""

    url_prefix = "/uct-theses/"

    PERMISSIONS_PRESETS = ["everyone"]

    schema = UctThesesSchema

    search = UctThesesSearchOptions

    record_cls = UctThesesRecord
    service_id = "uct_theses"

    components = [
        *RecordServiceConfig.components,
        CachingRelationsComponent,
        FilesOptionsComponent,
    ]

    model = "uct_theses"

    @property
    def links_item(self):
        return {
            "self": RecordLink("{self.url_prefix}{id}"),
            "files": RecordLink("{self.url_prefix}{id}/files"),
        }

    @property
    def links_search(self):
        return pagination_links("{self.url_prefix}{?args*}")
