from dataclasses import dataclass
import importlib_metadata
from typing import Any

from .abstract_record import AbstractRecord
from .abstract_record_source import AbstractRecordSource
from .exceptions import EntryPointNotFoundException, ExceptionMessage

@dataclass
class EntryPointsLoaderConfig:
    group: str
    record_source_name: str
    record_name: str

class EntryPointsLoader():
    def __init__(self, config: EntryPointsLoaderConfig):
        self._config = config
    
    def load_abstract_record_source(self, source_name_arg: str=None) -> AbstractRecordSource:
        """
        Tries to load an entry point that represents record source.
        """
        
        ep_record_source = self.__load(self._config.group, self._config.record_source_name, source_name_arg)

        if not ep_record_source:
            raise EntryPointNotFoundException(ExceptionMessage.AbstractSourceNotFound)

        record_source_class = ep_record_source.load()
        return record_source_class()
    
    def load_abstract_record(self, record_arg_name: str=None) -> AbstractRecord:
        """
        Tries to load an entry point that represents record.
        """
        
        ep_record = self.__load(self._config.group, self._config.record_name, record_arg_name)

        if not ep_record:
            raise EntryPointNotFoundException(ExceptionMessage.AbstractRecordNotFound)

        return ep_record.load()

    def __load(self, group: str, name: str, arg_name: str=None) -> Any | None:
        eps = importlib_metadata.entry_points(group=group)
        for ep in eps:
            if ep.name == arg_name or name:
                return ep

        raise ValueError(ExceptionMessage.EntryPointNotProvided)
