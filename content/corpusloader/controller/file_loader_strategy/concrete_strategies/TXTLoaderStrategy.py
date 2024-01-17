from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader, DataType
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class TXTLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader('document', DataType.STRING, True),
            CorpusHeader('filename', DataType.STRING, True),
            CorpusHeader('filepath', DataType.CATEGORY, True)
        ]

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        filepath: str = self.file_ref.resolve_real_file_path()
        with open(filepath) as f:
            document = f.read()

        included_headers: list[str] = [header.name for header in headers if header.include]
        file_data = {}
        if 'document' in included_headers:
            file_data['document'] = [document]
        if 'filename' in included_headers:
            file_data['filename'] = [self.file_ref.get_filename()]
        if 'filepath' in included_headers:
            file_data['filepath'] = [self.file_ref.get_full_path()]

        df: DataFrame = DataFrame(file_data)
        dtypes_applied_df: DataFrame = FileLoaderStrategy._apply_selected_dtypes(df, headers)

        return dtypes_applied_df
