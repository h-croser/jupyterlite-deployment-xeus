from abc import ABC, abstractmethod

from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader, FileReference


class FileLoaderStrategy(ABC):
    """
    An abstract class for loading files as DataFrame objects to be used in a DataFrameCorpus.
    A concrete class should extend this class for each file type that is supported.
    """
    def __init__(self, file_ref: FileReference):
        """
        :param file_ref: the FileReference object corresponding to the file to be loaded
        """
        self.file_ref: FileReference = file_ref

    @staticmethod
    def _apply_selected_dtypes(df: DataFrame, headers: list[CorpusHeader]) -> DataFrame:
        """
        Attempts to cast each column within the provided DataFrame to the data types specified in headers.
        :param df: the DataFrame object whose columns will be type cast
        :param headers: the CorpusHeader objects representing the columns of the DataFrame. CorpusHeader objects with
        include as False will be ignored.
        :return: the DataFrame with columns cast to the given data types
        """
        dtypes = {h.name: h.datatype.value for h in headers if h.include}

        return df.astype(dtype=dtypes)

    @abstractmethod
    def get_inferred_headers(self) -> list[CorpusHeader]:
        """
        Provides a list of CorpusHeader objects corresponding to the data found within the file.
        Some additional metadata headers may be provided not found within the file, such as filepath
        :return: a list of CorpusHeader objects corresponding to the data found within the file
        """
        raise NotImplementedError()

    @abstractmethod
    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        """
        Provides a DataFrame object containing the data from the loaded file.
        Columns of the DataFrame will be cast to the data types specified in the headers parameter.
        The DataFrame will exclude a column of data if its corresponding CorpusHeader object has include set to False
        :param headers: a list of CorpusHeader objects corresponding to the data found within the file
        :return: a DataFrame object corresponding to the loaded file and its provided CorpusHeader list
        """
        raise NotImplementedError()
