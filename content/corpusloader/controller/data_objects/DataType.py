from enum import Enum


class DataType(Enum):
    """
    Maps readable data type names to the pandas data types
    """
    STRING = 'string'
    INTEGER = 'Int64'
    FLOAT = 'Float64'
    BOOLEAN = 'boolean'
    DATETIME = 'datetime64[ns]'
    CATEGORY = 'category'
