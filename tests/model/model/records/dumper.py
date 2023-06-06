from invenio_records.dumpers import SearchDumper as InvenioElasticsearchDumper


class ModelDumper(InvenioElasticsearchDumper):
    """ModelRecord elasticsearch dumper."""
