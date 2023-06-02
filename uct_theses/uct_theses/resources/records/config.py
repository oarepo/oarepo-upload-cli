import importlib_metadata
from flask_resources import ResponseHandler
from invenio_records_resources.resources import RecordResourceConfig

from uct_theses.resources.records.ui import UctThesesUIJSONSerializer


class UctThesesResourceConfig(RecordResourceConfig):
    """UctThesesRecord resource config."""

    blueprint_name = "UctTheses"
    url_prefix = "/uct-theses/"

    @property
    def response_handlers(self):
        entrypoint_response_handlers = {}
        for x in importlib_metadata.entry_points(
            group="invenio.uct_theses.response_handlers"
        ):
            entrypoint_response_handlers.update(x.load())
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                UctThesesUIJSONSerializer()
            ),
            **super().response_handlers,
            **entrypoint_response_handlers,
        }
