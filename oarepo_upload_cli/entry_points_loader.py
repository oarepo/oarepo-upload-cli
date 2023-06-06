import importlib_metadata
from typing import Any

from .exceptions import EntryPointNotFoundException, ExceptionMessage

class EntryPointsLoader():
    def __init__(self):
        self._group = 'oarepo_upload_cli.dependencies'
    
    def load_entry_point(self, name: str, default=None):
        """
        Tries to load an entry point given by argument value or 
        """
        ep = self.__load(self._group, name)
        
        if not ep:
            if default:
                return default
            
            raise EntryPointNotFoundException()
        
        return ep.load()
    
    def __load(self, group: str, name: str) -> Any | None:
        # TODO name.
        eps = importlib_metadata.entry_points(group=group)
        for ep in eps:
            if ep.name == name:
                return ep

        raise ValueError(ExceptionMessage.EntryPointNotProvided.value)