import marshmallow as ma
import marshmallow.fields as ma_fields
import marshmallow.validate as ma_valid
from invenio_records_resources.services.records.schema import BaseRecordSchema
from invenio_records_resources.services.records.schema import (
    BaseRecordSchema as InvenioBaseRecordSchema,
)
from marshmallow import ValidationError
from marshmallow import validates as ma_validates
from marshmallow_utils.fields import EDTFDateString


class ModelMetadataSchema(
    ma.Schema,
):
    """ModelMetadataSchema schema."""

    updated = EDTFDateString(required=True)


class ModelSchema(
    BaseRecordSchema,
):
    """ModelSchema schema."""

    metadata = ma_fields.Nested(ModelMetadataSchema)

    created = ma_fields.Date(dump_only=True)

    updated = ma_fields.Date(dump_only=True)
