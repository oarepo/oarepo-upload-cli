import importlib_metadata
from flask_resources import ResponseHandler
from invenio_records_resources.resources import FileResourceConfig

from uct_theses.resources.files.ui import UctThesesFileUIJSONSerializer


class UctThesesFileResourceConfig(FileResourceConfig):
    """UctThesesFileRecord resource config."""

    blueprint_name = "UctThesesFile"
    url_prefix = "/uct-theses/<pid_value>"

    @property
    def response_handlers(self):
        entrypoint_response_handlers = {}
        for x in importlib_metadata.entry_points(
            group="invenio.uct_theses.response_handlers"
        ):
            entrypoint_response_handlers.update(x.load())
        return {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                UctThesesFileUIJSONSerializer()
            ),
            **super().response_handlers,
            **entrypoint_response_handlers,
        }
