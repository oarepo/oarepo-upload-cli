from marshmallow import fields as ma_fields
from nr_metadata.documents.services.records.ui_schema import (
    NRDocumentMetadataUISchema,
)
from oarepo_runtime.ui.marshmallow import InvenioUISchema


class UctThesesUISchema(InvenioUISchema):
    """UctThesesUISchema schema."""

    metadata = ma_fields.Nested(lambda: NRDocumentMetadataUISchema())
