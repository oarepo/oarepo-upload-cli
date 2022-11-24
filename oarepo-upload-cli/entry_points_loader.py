import pkg_resources
from typing import Any, Union, NoReturn

from abstract_record import AbstractRecordInterface
from abstract_record_source import AbstractRecordSourceInterface

class EntryPointsLoader():
    def load_abstract_record_source(self, source_name_arg: str) -> Union[AbstractRecordSourceInterface, NoReturn]:
        group, name = 'dependencies', 'abstract_record_source'

        abstract_record_source = self.__load(group, name, source_name_arg)

        if not abstract_record_source:
            # raise an exception that abstract source is not defined
            pass

        if not issubclass(abstract_record_source, AbstractRecordSourceInterface):
            raise RuntimeError('Provided abstract record source does not correctly implement required interface.')
        
        return abstract_record_source

    
    def load_abstract_record(self, record_name_args: str) -> Union[AbstractRecordInterface, NoReturn]:
        group, name = 'dependencies', 'abstract_record'

        abstract_record = self.__load(group, name, record_name_args)

        if not abstract_record:
            # raise an exception that abstract record is not defined
            pass

        if not issubclass(abstract_record, AbstractRecordInterface):
            raise RuntimeError('Abstract record entrypoint does not correctly implement required interface.')
        
        return abstract_record

    def __load(self, group: str, name: str, arg_name: str = None) -> Union[Any, NoReturn]:
        eps = list(pkg_resources.iter_entry_points(group, name))

        if not eps:
            raise ValueError('Entry point not provided')
        
        if len(eps) > 1 and not arg_name:
            raise ValueError('Multiple entry points present, can not choose one')
    
        for ep in eps:
            if ep.name == arg_name:
                return ep
            
        return None
    
