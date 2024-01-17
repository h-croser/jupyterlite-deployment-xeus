from panel import Tabs, Column, Row

from corpusloader.controller import Controller
from corpusloader.controller.data_objects import FileReference
from corpusloader.view.gui import AbstractWidget, FileLoaderWidget, OniLoaderWidget, CorpusInfoWidget


class ViewWrapperWidget(AbstractWidget):
    """
    A wrapper class that holds different loading method interfaces within a Tab
    """
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.file_loader: AbstractWidget = FileLoaderWidget(self, controller)
        self.oni_loader: AbstractWidget = OniLoaderWidget(controller)
        self.corpus_display: AbstractWidget = CorpusInfoWidget(controller)
        self.display_idx: int = 2

        self.panel = Tabs(("File Loader", self.file_loader),
                          ("Oni Loader", self.oni_loader),
                          ("Corpus Overview", self.corpus_display))
        self.children = [self.file_loader, self.oni_loader, self.corpus_display]

    def update_display(self):
        pass

    def load_corpus_from_filepaths(self, filepath_ls: list[FileReference]) -> bool:
        success = self.controller.load_corpus_from_filepaths(filepath_ls)
        self.update_displays()
        return success

    def load_meta_from_filepaths(self, filepath_ls: list[FileReference]) -> bool:
        success = self.controller.load_meta_from_filepaths(filepath_ls)
        self.update_displays()
        return success

    def build_corpus(self, corpus_name: str):
        success: bool = self.controller.build_corpus(corpus_name)
        if success:
            self.panel.active = self.display_idx
            self.update_displays()
