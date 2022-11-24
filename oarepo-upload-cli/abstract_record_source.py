class AbstractRecordSourceMeta(type):
    """
    Abstract record source metaclass that is used for source creation.
    """
    def __instancecheck__(cls, instance) -> bool:
        return cls.__subclasscheck__(type(instance))
    
    def __subclasscheck__(cls, subclass) -> bool:
        return hasattr(subclass, 'get_records') and callable(subclass.get_records)
    
class AbstractRecordSource(metaclass=AbstractRecordSourceMeta):
    """
    Interface for concrete record provider.
    """
    pass