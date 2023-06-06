from invenio_records_resources.services import FileLink, FileServiceConfig, RecordLink
from oarepo_runtime.relations.components import CachingRelationsComponent

from uct_theses.records.api import UctThesesRecord
from uct_theses.services.files.schema import UctThesesFileSchema
from uct_theses.services.records.permissions import UctThesesPermissionPolicy


class UctThesesFileServiceConfig(FileServiceConfig):
    """UctThesesFileRecord service config."""

    url_prefix = "/uct-theses/<pid_value>"

    permission_policy_cls = UctThesesPermissionPolicy

    schema = UctThesesFileSchema

    record_cls = UctThesesRecord
    service_id = "uct_theses_file"

    components = [*FileServiceConfig.components, CachingRelationsComponent]

    model = "uct_theses"

    # todo remove links property
    @property
    def file_links_list(self):
        return {
            "self": RecordLink("{self.url_prefix}{id}/files"),
        }

    @property
    def file_links_item(self):
        return {
            "self": FileLink("{self.url_prefix}{id}/files/{key}"),
            "content": FileLink("{self.url_prefix}{id}/files/{key}/content"),
            "commit": FileLink("{self.url_prefix}{id}/files/{key}/commit"),
        }
