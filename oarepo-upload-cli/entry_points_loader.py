from importlib.metadata import entry_points
from typing import Any, NoReturn

from abstract_record import AbstractRecord
from abstract_record_source import AbstractRecordSource

class EntryPointNotFoundException(Exception):
    """
    Raise when an entry point is not defined.
    """
    pass

class EntryPointsLoader():
    def load_abstract_record_source(self, source_name_arg: str = None) -> AbstractRecordSource | NoReturn:
        group, name = 'dependencies', 'oarepo-upload-source'

        abstract_record_source = self.__load(group, name, source_name_arg)

        if not abstract_record_source:
            raise EntryPointNotFoundException('Abstract record source')

        if not issubclass(abstract_record_source, AbstractRecordSourceInterface):
            raise RuntimeError('Provided abstract record source does not correctly implement required interface.')
        
        return abstract_record_source.load()

    
    def load_abstract_record(self, group: str, name: str, record_arg_name: str = None) -> AbstractRecord | NoReturn:
        group, name = 'dependencies', 'oarepo-upload-record'

        abstract_record = self.__load(group, name, record_arg_name)

        if not abstract_record:
            raise EntryPointNotFoundException('Abstract record')

        if not issubclass(abstract_record, AbstractRecordInterface):
            raise RuntimeError('Abstract record entrypoint does not correctly implement required interface.')
        
        return abstract_record.load()

    def __load(self, group: str, name: str, arg_name: str = None) -> Any | NoReturn:
        eps = entry_points().select(group=group, name=name)

        if not eps:
            raise ValueError('Entry point not provided')
        
        if len(eps) == 1 and not arg_name:
            # user wants the same entry point as it is defined
            return eps[0]
        
        if len(eps) == 1 and arg_name and eps[0].name != arg_name:
            # user wants an entry point that is not loaded
            raise EntryPointNotFoundException(f'Entry point {arg_name} was not found.')

        if not arg_name:
            raise ValueError('Multiple entry points present, can not choose one')
    
        for ep in eps:
            if ep.name == arg_name:
                return ep
            
        return None
    
