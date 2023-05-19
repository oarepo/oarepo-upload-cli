from dataclasses import dataclass
import importlib_metadata
from typing import Any

from .abstract_record_source import AbstractRecordSource
from .exceptions import EntryPointNotFoundException, ExceptionMessage

@dataclass
class EntryPointsLoaderConfig:
    group: str
    source: str

class EntryPointsLoader():
    def __init__(self, config: EntryPointsLoaderConfig):
        self._config = config
    
    def load_abstract_record_source(self, source_arg: str=None) -> AbstractRecordSource:
        """
        Tries to load an entry point that represents record source.
        """
        
        source = source_arg or self._config.source
        
        ep_record_source = self.__load(self._config.group, source)

        if not ep_record_source:
            raise EntryPointNotFoundException(ExceptionMessage.AbstractSourceNotFound)

        record_source_class = ep_record_source.load()
        return record_source_class()

    def __load(self, group: str, name: str) -> Any | None:
        # TODO name.
        eps = importlib_metadata.entry_points(group=group)
        for ep in eps:
            if ep.name == name:
                return ep

        raise ValueError(ExceptionMessage.EntryPointNotProvided)