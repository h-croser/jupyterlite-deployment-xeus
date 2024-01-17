from glob import glob
from os.path import join, isdir, basename, dirname
from typing import Optional, Callable

from atap_corpus.corpus.corpus import DataFrameCorpus
from pandas import DataFrame

from corpusloader.controller.FileLoaderService import FileLoaderService, FileLoadError
from corpusloader.controller.OniAPIService import OniAPIService
from corpusloader.controller.data_objects import FileReference, ZipFileReference
from corpusloader.controller.data_objects.CorpusHeader import CorpusHeader
from corpusloader.controller.data_objects.DataType import DataType
from corpusloader.controller.file_loader_strategy.FileLoaderFactory import ValidFileType
from corpusloader.view.notifications import NotifierService


class Controller:
    """
    Provides methods for indirection between the corpus loading logic and the user interface
    Holds a reference to the corpus once built.
    The build_callback_fn will be called when the corpus is built (can be set using set_build_callback()).
    """
    def __init__(self, notifier_service: NotifierService, root_directory: str):
        self.root_directory: str = root_directory

        self.file_loader_service: FileLoaderService = FileLoaderService()
        self.oni_api_service: OniAPIService = OniAPIService()
        self.notifier_service: NotifierService = notifier_service

        self.text_header: Optional[CorpusHeader] = None
        self.corpus_link_header: Optional[CorpusHeader] = None
        self.meta_link_header: Optional[CorpusHeader] = None

        self.corpus_headers: list[CorpusHeader] = []
        self.meta_headers: list[CorpusHeader] = []

        self.corpus: Optional[DataFrameCorpus] = None
        self.corpus_info: Optional[dict] = None

        self.build_callback_fn: Optional[Callable] = None
        self.build_callback_args: list = []
        self.build_callback_kwargs: dict = {}

    def display_error(self, error_msg: str):
        self.notifier_service.notify_error(error_msg)

    def display_success(self, success_msg: str):
        self.notifier_service.notify_success(success_msg)

    def set_build_callback(self, callback: Callable, *args, **kwargs):
        if not callable(callback):
            raise ValueError("Provided callback function must be a callable")
        self.build_callback_fn = callback
        self.build_callback_args = args
        self.build_callback_kwargs = kwargs

    def get_corpus(self) -> Optional[DataFrameCorpus]:
        return self.corpus

    def get_loaded_corpus_df(self) -> Optional[DataFrame]:
        if self.corpus is None:
            return None
        return self.corpus.to_dataframe()

    def load_corpus_from_filepaths(self, filepath_ls: list[FileReference]) -> bool:
        for filepath in filepath_ls:
            try:
                self.file_loader_service.add_corpus_filepath(filepath)
                self.corpus_headers = self.file_loader_service.get_inferred_corpus_headers()
            except FileLoadError as e:
                self.file_loader_service.remove_corpus_filepath(filepath)
                self.display_error(str(e))
                return False

        self.display_success("Corpus files loaded successfully")
        return True

    def load_meta_from_filepaths(self, filepath_ls: list[FileReference]) -> bool:
        for filepath in filepath_ls:
            try:
                self.file_loader_service.add_meta_filepath(filepath)
                self.meta_headers = self.file_loader_service.get_inferred_meta_headers()
            except FileLoadError as e:
                self.file_loader_service.remove_meta_filepath(filepath)
                self.display_error(str(e))
                return False

        self.display_success("Metadata files loaded successfully")
        return True

    def build_corpus(self, corpus_name: str) -> bool:
        if self.is_meta_added():
            if (self.corpus_link_header is None) or (self.meta_link_header is None):
                self.display_error("Cannot build without link headers set. Select a corpus header and a meta header as linking headers in the dropdowns")
                return False

        try:
            self.corpus = self.file_loader_service.build_corpus(corpus_name, self.corpus_headers,
                                                                self.meta_headers, self.text_header,
                                                                self.corpus_link_header, self.meta_link_header)
        except FileLoadError as e:
            self.display_error(str(e))
            return False

        self.set_corpus_info()
        self.display_success("Corpus built successfully")

        if self.build_callback_fn is not None:
            self.build_callback_fn(*self.build_callback_args, **self.build_callback_kwargs)

        return True

    def set_corpus_info(self):
        if self.corpus is None:
            self.corpus_info = None
            return

        corpus_info: dict = {}
        corpus_as_df: DataFrame = self.corpus.to_dataframe()

        corpus_info["name"] = self.corpus.name
        corpus_info["rows"] = len(self.corpus)

        corpus_info["files"] = str(self.get_loaded_file_count())

        headers = []
        dtypes = []
        for header_name, dtype_obj in corpus_as_df.dtypes.items():
            dtypes.append(str(dtype_obj).upper())
            headers.append(header_name)
        corpus_info["headers"] = headers
        corpus_info["dtypes"] = dtypes

        self.corpus_info = corpus_info

    def get_corpus_info(self) -> Optional[dict[str, str]]:
        return self.corpus_info

    def get_loaded_file_counts(self) -> dict[str, int]:
        corpus_file_set = set(self.file_loader_service.get_loaded_corpus_files())
        meta_file_set = set(self.file_loader_service.get_loaded_meta_files())
        file_set = corpus_file_set | meta_file_set

        file_counts: dict[str, int] = {"Total files": len(file_set)}
        for file_ref in file_set:
            extension = file_ref.get_extension().upper()
            if file_counts.get(extension) is None:
                file_counts[extension] = 1
            else:
                file_counts[extension] += 1

        return file_counts

    def unload_filepaths(self, filepath_ls: list[FileReference]):
        for filepath in filepath_ls:
            self.file_loader_service.remove_meta_filepath(filepath)
            self.file_loader_service.remove_corpus_filepath(filepath)

        if len(self.file_loader_service.get_loaded_corpus_files()) == 0:
            self.text_header = None
            self.corpus_headers = []
            self.corpus_link_header = None
        if len(self.file_loader_service.get_loaded_meta_files()) == 0:
            self.meta_headers = []
            self.meta_link_header = None

    def unload_all(self):
        self.file_loader_service.remove_all_files()

        self.text_header = None
        self.corpus_headers = []
        self.meta_headers = []
        self.corpus_link_header = None
        self.meta_link_header = None

    def get_loaded_corpus_files(self) -> list[FileReference]:
        return self.file_loader_service.get_loaded_corpus_files()

    def get_loaded_meta_files(self) -> list[FileReference]:
        return self.file_loader_service.get_loaded_meta_files()

    def get_corpus_headers(self) -> list[CorpusHeader]:
        return self.corpus_headers

    def get_meta_headers(self) -> list[CorpusHeader]:
        return self.meta_headers

    def get_inferred_corpus_headers(self) -> list[CorpusHeader]:
        return self.file_loader_service.get_inferred_corpus_headers()

    def get_inferred_meta_headers(self) -> list[CorpusHeader]:
        return self.file_loader_service.get_inferred_meta_headers()

    def get_text_header(self) -> Optional[CorpusHeader]:
        return self.text_header

    def get_corpus_link_header(self) -> Optional[CorpusHeader]:
        return self.corpus_link_header

    def get_meta_link_header(self) -> Optional[CorpusHeader]:
        return self.meta_link_header

    def get_all_datatypes(self) -> list[str]:
        return [d.name for d in DataType]

    def get_valid_filetypes(self) -> list[str]:
        return [ft.name for ft in ValidFileType]

    def is_corpus_added(self) -> bool:
        return len(self.corpus_headers) > 0

    def is_meta_added(self) -> bool:
        return len(self.meta_headers) > 0

    def get_loaded_file_count(self) -> int:
        corpus_file_set = set(self.file_loader_service.get_loaded_corpus_files())
        meta_file_set = set(self.file_loader_service.get_loaded_meta_files())
        file_set = corpus_file_set | meta_file_set

        return len(file_set)

    def update_corpus_header(self, header: CorpusHeader, include: Optional[bool], datatype_name: Optional[str]):
        if include is not None:
            header.include = include
        if datatype_name is not None:
            header.datatype = DataType[datatype_name]

        for i, corpus_header in enumerate(self.corpus_headers):
            if header == corpus_header:
                self.corpus_headers[i] = header

    def update_meta_header(self, header: CorpusHeader, include: Optional[bool], datatype_name: Optional[str]):
        if include is not None:
            header.include = include
        if datatype_name is not None:
            header.datatype = DataType[datatype_name]

        for i, meta_header in enumerate(self.meta_headers):
            if header == meta_header:
                self.meta_headers[i] = header

    def set_text_header(self, text_header: Optional[str]):
        if text_header is None:
            self.text_header = None
            return

        for header in self.corpus_headers:
            if header.name == text_header:
                self.text_header = header
                header.datatype = DataType['STRING']
                header.include = True
                return

    def set_corpus_link_header(self, link_header_name: Optional[str]):
        for header in self.corpus_headers:
            if header.name == link_header_name:
                self.corpus_link_header = header
                header.include = True
                return
        self.corpus_link_header = None

    def set_meta_link_header(self, link_header_name: Optional[str]):
        for header in self.meta_headers:
            if header.name == link_header_name:
                self.meta_link_header = header
                header.include = True
                return
        self.meta_link_header = None

    def retrieve_all_files(self) -> list[FileReference]:
        all_relative_paths: list[str] = glob("**", root_dir=self.root_directory, recursive=True)
        all_full_paths: list[str] = []
        for path in all_relative_paths:
            full_path = join(self.root_directory, path)
            if not isdir(full_path):
                all_full_paths.append(join(self.root_directory, path))

        all_file_refs: list[FileReference] = []
        for idx, full_path in enumerate(all_full_paths):
            if full_path.endswith('.zip'):
                zip_file_refs: list[FileReference] = ZipFileReference.get_zip_internal_file_refs(self.root_directory, full_path)
                all_file_refs.extend(zip_file_refs)
            else:
                file_ref = FileReference(self.root_directory, dirname(full_path), basename(full_path))
                all_file_refs.append(file_ref)

        all_file_refs.sort(key=lambda ref: ref.get_full_path())

        return all_file_refs
