import importlib_metadata

from .exceptions import ExceptionMessage


class EntryPointsLoader:
    def __init__(self):
        self._group = "oarepo_upload_cli.dependencies"

    def load_entry_point(self, name: str, default=None):
        """
        Tries to load an entry point given by argument value or
        """
        eps = importlib_metadata.entry_points(group=self._group)
        for ep in eps:
            if ep.name == name:
                return ep.load()
        if default:
            return default
        raise ValueError(
            f"{ExceptionMessage.EntryPointNotProvided.value}: group '{self._group}', name '{name}'"
        )
