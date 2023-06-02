from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess
from invenio_records_resources.services.files.generators import AnyUserIfFileIsLocal


class UctThesesPermissionPolicy(RecordPermissionPolicy):
    """uct_theses.records.api.UctThesesRecord permissions."""

    can_search = [SystemProcess(), AnyUser()]
    can_read = [SystemProcess(), AnyUser()]
    can_create = [SystemProcess(), AnyUser()]
    can_update = [SystemProcess(), AnyUser()]
    can_delete = [SystemProcess(), AnyUser()]
    can_manage = [SystemProcess(), AnyUser()]

    can_create_files = [AnyUser(), SystemProcess()]
    can_set_content_files = [AnyUserIfFileIsLocal(), SystemProcess(), AnyUser()]
    can_get_content_files = [AnyUserIfFileIsLocal(), SystemProcess(), AnyUser()]
    can_commit_files = [AnyUserIfFileIsLocal(), SystemProcess(), AnyUser()]
    can_read_files = [AnyUser(), SystemProcess()]
    can_update_files = [AnyUser(), SystemProcess()]
    can_delete_files = [AnyUser(), SystemProcess()]
