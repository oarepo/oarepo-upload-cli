from dataclasses import dataclass
import importlib_metadata
from typing import Any

from .abstract_repository_records_handler import AbstractRepositoryRecordsHandler
from .abstract_record_source import AbstractRecordSource
from .exceptions import EntryPointNotFoundException, ExceptionMessage

@dataclass
class EntryPointsLoaderConfig:
    group: str
    source: str
    repo_handler: str

class EntryPointsLoader():
    def __init__(self, config: EntryPointsLoaderConfig):
        self._config = config
    
    def load_entry_point(self, config_value: str, arg: str=None):
        """
        Tries to load an entry point given by argument value or 
        """
        name = arg or config_value
        
        ep = self.__load(self._config.group, name)
        
        if not ep:
            raise EntryPointNotFoundException(ExceptionMessage.EntryPointNotProvided)
        
        return ep.load()
    
    def __load(self, group: str, name: str) -> Any | None:
        # TODO name.
        eps = importlib_metadata.entry_points(group=group)
        for ep in eps:
            if ep.name == name:
                return ep

        raise ValueError(ExceptionMessage.EntryPointNotProvided)