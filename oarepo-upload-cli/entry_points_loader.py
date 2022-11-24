import pkg_resources
from typing import Any, NoReturn

from abstract_record import AbstractRecordInterface
from abstract_record_source import AbstractRecordSourceInterface

class EntryPointNotFoundException(Exception):
    """
    Raise when an entry point is not defined.
    """
    pass

class EntryPointsLoader():
    def load_abstract_record_source(self, source_name_arg: str = None) -> AbstractRecordSourceInterface | NoReturn:
        group, name = 'dependencies', 'abstract_record_source'

        abstract_record_source = self.__load(group, name, source_name_arg)

        if not abstract_record_source:
            raise EntryPointNotFoundException('Abstract record source')

        if not issubclass(abstract_record_source, AbstractRecordSourceInterface):
            raise RuntimeError('Provided abstract record source does not correctly implement required interface.')
        
        return abstract_record_source.load()

    
    def load_abstract_record(self, record_name_args: str = None) -> AbstractRecordInterface | NoReturn:
        group, name = 'dependencies', 'abstract_record'

        abstract_record = self.__load(group, name, record_name_args)

        if not abstract_record:
            raise EntryPointNotFoundException('Abstract record')

        if not issubclass(abstract_record, AbstractRecordInterface):
            raise RuntimeError('Abstract record entrypoint does not correctly implement required interface.')
        
        return abstract_record.load()

    def __load(self, group: str, name: str, arg_name: str = None) -> Any | NoReturn:
        eps = list(pkg_resources.iter_entry_points(group, name))

        if not eps:
            raise ValueError('Entry point not provided')
        
        if len(eps) > 1 and not arg_name:
            raise ValueError('Multiple entry points present, can not choose one')
    
        for ep in eps:
            if ep.name == arg_name:
                return ep
            
        return None
    
