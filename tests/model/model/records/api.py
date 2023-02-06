from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ConstantField, RelationsField
from invenio_records_resources.records.api import Record as InvenioBaseRecord
from invenio_records_resources.records.systemfields import IndexField
from invenio_records_resources.records.systemfields.pid import PIDField, PIDFieldContext
from model.records.dumper import ModelDumper
from model.records.models import ModelMetadata


class ModelRecord(InvenioBaseRecord):
    model_cls = ModelMetadata
    schema = ConstantField("$schema", "local://model-1.0.0.json")
    index = IndexField("model-model-1.0.0")

    pid = PIDField(
        create=True, provider=RecordIdProviderV2, context_cls=PIDFieldContext
    )

    dumper_extensions = []
    dumper = ModelDumper(extensions=dumper_extensions)
