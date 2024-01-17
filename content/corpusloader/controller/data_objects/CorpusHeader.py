from corpusloader.controller.data_objects import DataType


class CorpusHeader:
    """
    Represents a column before the corpus is built.
    Holds the name, intended datatype, and whether to include the header.
    Also behaves as a Value Object, where the unique value is the name for equality checks and hashing.
    """
    def __init__(self, name: str, datatype: DataType, include: bool):
        self.name: str = name
        self.datatype: DataType = datatype
        self.include: bool = include

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"CorpusHeader: {self.name} [{self.datatype.value}]"

    def __eq__(self, other):
        if type(other) is not CorpusHeader:
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
