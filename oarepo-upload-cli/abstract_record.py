class AbstractRecordMeta(type):
    """
    Abstract record metaclass that is used for record creation.
    """
    def __instancecheck__(cls, instance) -> bool:
        return cls.__subclasscheck__(type(instance))
    
    def __subclasscheck__(cls, subclass) -> bool:
        return hasattr(subclass, 'get_metadata') and callable(subclass.get_metadata)
    
class AbstractRecordInterface(metaclass=AbstractRecordMeta):
    """
    Interface for concrete record.
    """
    pass