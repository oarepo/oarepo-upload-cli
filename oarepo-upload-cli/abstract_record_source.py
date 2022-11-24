class AbstractRecordSourceMeta(type):
    """
    Abstract record source metaclass that is used for source creation.
    """
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))
    
    def __subclasscheck__(cls, subclass):
        return hasattr(subclass, 'get_records') and callable(subclass.get_records)
    
class AbstractRecordSourceInterface(metaclass=AbstractRecordSourceMeta):
    """
    Interface for concrete record provider.
    """
    pass