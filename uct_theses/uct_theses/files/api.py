from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields.pid import PIDField, PIDFieldContext

from uct_theses.files.dumper import UctThesesFileDumper
from uct_theses.files.models import UctThesesFileMetadata


class UctThesesFileIdProvider(RecordIdProviderV2):
    pid_type = "ct_hss"


class UctThesesFileRecord(FileRecord):
    model_cls = UctThesesFileMetadata

    pid = PIDField(
        provider=UctThesesFileIdProvider, context_cls=PIDFieldContext, create=True
    )

    dumper_extensions = []
    dumper = UctThesesFileDumper(extensions=dumper_extensions)
    record_cls = None  # is defined below
