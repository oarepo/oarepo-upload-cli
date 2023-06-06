from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess, AuthenticatedUser
from invenio_records_resources.services.files.generators import AnyUserIfFileIsLocal


class UctThesesPermissionPolicy(RecordPermissionPolicy):
    """uct_theses.records.api.UctThesesRecord permissions."""

    can_search = [SystemProcess(), AnyUser()]
    can_read = [SystemProcess(), AnyUser()]
    can_create = [SystemProcess(), AuthenticatedUser()]
    can_update = [SystemProcess(), AuthenticatedUser()]
    can_delete = [SystemProcess(), AuthenticatedUser()]
    can_manage = [SystemProcess(), AuthenticatedUser()]

    can_create_files = [AuthenticatedUser(), SystemProcess()]
    can_set_content_files = [AnyUserIfFileIsLocal(), SystemProcess(), AuthenticatedUser()]
    can_get_content_files = [AnyUserIfFileIsLocal(), SystemProcess(), AnyUser()]
    can_commit_files = [AnyUserIfFileIsLocal(), SystemProcess(), AuthenticatedUser()]
    can_read_files = [AnyUser(), SystemProcess()]
    can_update_files = [AuthenticatedUser(), SystemProcess()]
    can_delete_files = [AuthenticatedUser(), SystemProcess()]