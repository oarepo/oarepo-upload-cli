from invenio_records_resources.services import SearchOptions as InvenioSearchOptions

from . import facets


def _(x):
    """Identity function for string extraction."""
    return x


class ModelSearchOptions(InvenioSearchOptions):
    """ModelRecord search options."""

    facets = {
        "metadata_updated": facets.metadata_updated,
        "_id": facets._id,
        "created": facets.created,
        "updated": facets.updated,
        "_schema": facets._schema,
        "max_date": facets.max_date,
    }
    sort_options = {
        **InvenioSearchOptions.sort_options,
    }
