from invenio_records_resources.services.records.schema import (
    BaseRecordSchema as InvenioBaseRecordSchema,
)
from marshmallow import fields as ma_fields
from marshmallow.utils import get_value
from nr_metadata.documents.services.records.schema import NRDocumentMetadataSchema

from uct_theses.services.files.schema import FilesOptionsSchema


class UctThesesSchema(InvenioBaseRecordSchema):
    """UctThesesSchema schema."""

    metadata = ma_fields.Nested(lambda: NRDocumentMetadataSchema())
    files = ma_fields.Nested(FilesOptionsSchema, load_default={"enabled": True})

    # todo this needs to be generated for [default preview] to work
    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        if attr == "files":
            return getattr(obj, attr, default)
        else:
            return get_value(obj, attr, default)
