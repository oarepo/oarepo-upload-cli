from invenio_records_resources.resources import RecordResource as InvenioRecordResource


class ModelResource(InvenioRecordResource):
    """ModelRecord resource."""

    # here you can for example redefine
    # create_url_rules function to add your own rules