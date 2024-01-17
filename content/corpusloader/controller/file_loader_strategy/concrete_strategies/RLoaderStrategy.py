from pandas import DataFrame, concat
from pyreadr import list_objects, read_r
from pyreadr.librdata import PyreadrError, LibrdataError

from corpusloader.controller.data_objects import CorpusHeader, DataType
from corpusloader.controller.file_loader_strategy.FileLoadError import FileLoadError
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class RLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        filepath: str = self.file_ref.resolve_real_file_path()
        try:
            file_objects: list[dict] = list_objects(filepath)
        except (PyreadrError, LibrdataError) as e:
            raise FileLoadError(f"Error loading R file: {str(e)}")

        if len(file_objects) == 0:
            return []

        columns = file_objects[0].get('columns')
        for file_object in file_objects[1:]:
            if file_object.get('columns') != columns:
                raise FileLoadError(f"Incompatible headers within loaded RData objects")

        headers: list[CorpusHeader] = []
        dtype: DataType = DataType['STRING']
        for col_name in columns:
            headers.append(CorpusHeader(col_name, dtype, True))

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        filepath: str = self.file_ref.resolve_real_file_path()
        try:
            object_df_dict: dict = read_r(filepath)
        except (PyreadrError, LibrdataError) as e:
            raise FileLoadError(f"Error loading R file: {str(e)}")

        df_list = object_df_dict.values()
        concat_df: DataFrame = concat(df_list, ignore_index=True)
        excluded_headers: list[str] = [header.name for header in headers if not header.include]
        df = concat_df.drop(excluded_headers, axis='columns')
        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_dtypes(df, headers)

        return dtypes_applied_df
