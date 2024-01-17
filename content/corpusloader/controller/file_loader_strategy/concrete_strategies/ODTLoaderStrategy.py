from odf import text, teletype
from odf.opendocument import load
from pandas import DataFrame

from corpusloader.controller.data_objects import CorpusHeader, DataType, FileReference
from corpusloader.controller.file_loader_strategy.FileLoaderStrategy import FileLoaderStrategy


class ODTLoaderStrategy(FileLoaderStrategy):
    def get_inferred_headers(self) -> list[CorpusHeader]:
        headers: list[CorpusHeader] = [
            CorpusHeader('document', DataType.STRING, True),
            CorpusHeader('filename', DataType.STRING, True),
            CorpusHeader('filepath', DataType.CATEGORY, True)
        ]

        return headers

    def get_dataframe(self, headers: list[CorpusHeader]) -> DataFrame:
        filepath: str = self.file_ref.resolve_real_file_path()
        odt_doc = load(filepath)
        document = ''
        for element in odt_doc.getElementsByType(text.P):
            document += teletype.extractText(element)

        included_headers: list[str] = [header.name for header in headers if header.include]
        file_data = {}
        if 'document' in included_headers:
            file_data['document'] = [document]
        if 'filename' in included_headers:
            file_data['filename'] = [self.file_ref.get_filename()]
        if 'filepath' in included_headers:
            file_data['filepath'] = [self.file_ref.get_full_path()]

        return DataFrame(file_data)
