import marshmallow as ma
from marshmallow import fields as ma_fields
from oarepo_runtime.ui import marshmallow as l10n


class UctThesesFileUISchema(ma.Schema):
    """UctThesesFileUISchema schema."""

    _id = ma_fields.String(data_key="id", attribute="id")
    created = l10n.LocalizedDate()
    updated = l10n.LocalizedDate()
    _schema = ma_fields.String(data_key="$schema", attribute="$schema")
