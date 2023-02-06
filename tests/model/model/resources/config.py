from invenio_records_resources.resources import (
    RecordResourceConfig as InvenioRecordResourceConfig,
)


class ModelResourceConfig(InvenioRecordResourceConfig):
    """ModelRecord resource config."""

    blueprint_name = "Model"
    url_prefix = "/model/"
