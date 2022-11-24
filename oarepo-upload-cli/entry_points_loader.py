import pkg_resources
from typing import Any, Union

from abstract_record import AbstractRecordInterface
from abstract_record_source import AbstractRecordSourceInterface

class EntryPointsLoader():
    def load_abstract_source(self, source_name_arg: str) -> Union[AbstractRecordSourceInterface, None]:
        group, name = 'dependencies', 'abstract_record_source'

        return self.__load(group, name, source_name_arg)
    
    def load_abstract_record(self, record_name_args: str) -> Union[AbstractRecordInterface, None]:
        group, name = 'dependencies', 'abstract_record'

        return self.__load(group, name, record_name_args)

    def __load(self, group: str, name: str, arg_name: str = None) -> Union[Any, None]:
        eps = list(pkg_resources.iter_entry_points(group, name))

        if not eps:
            raise ValueError('Entry point not provided')
        
        if len(eps) > 1 and not arg_name:
            raise ValueError('Multiple entry points present, can not choose one')
    
        for ep in eps:
            if ep.name == arg_name:
                return ep
            
        return None
    
