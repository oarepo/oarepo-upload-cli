import importlib_metadata
from typing import Any

from abstract_record import AbstractRecord
from abstract_record_source import AbstractRecordSource
from exceptions import EntryPointNotFoundException, ExceptionMessage

class EntryPointsLoader():
    def load_abstract_record_source(self, source_name_arg: str=None) -> AbstractRecordSource:
        """
        Tries to load an entry point that represents record source.
        """
        group, name = 'oarepo_upload_cli.dependencies', 'oarepo_upload_source'

        ep_record_source = self.__load(group, name, source_name_arg)

        if not ep_record_source:
            raise EntryPointNotFoundException(ExceptionMessage.AbstractSourceNotFound)
        
        return ep_record_source.load()

    
    def load_abstract_record(self, record_arg_name: str=None) -> AbstractRecord:
        """
        Tries to load an entry point that represents record.
        """
        group, name = 'oarepo_upload_cli.dependencies', 'oarepo_upload_record'

        ep_record = self.__load(group, name, record_arg_name)

        if not ep_record:
            raise EntryPointNotFoundException(ExceptionMessage.AbstractRecordNotFound)

        return ep_record.load()

    def __load(self, group: str, name: str, arg_name: str=None) -> Any | None:
        eps = importlib_metadata.entry_points().select(group=group, name=name)

        if not eps:
            raise ValueError(ExceptionMessage.EntryPointNotProvided)
        
        if len(eps) == 1 and not arg_name:
            # user requested the same entry point as it is defined
            return eps[0]
        
        if len(eps) == 1 and arg_name and eps[0].name != arg_name:
            # user requested an entry point that is not loaded
            raise EntryPointNotFoundException(ExceptionMessage.EntryPointNotProvided)

        if not arg_name:
            raise ValueError(ExceptionMessage.MultipleEntryPoints)
    
        for ep in eps:
            if ep.name == arg_name:
                return ep
            
        return None
    
