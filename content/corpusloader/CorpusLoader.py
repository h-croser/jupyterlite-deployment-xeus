from typing import Optional, Callable

import panel
from atap_corpus.corpus.corpus import DataFrameCorpus
from panel.viewable import Viewer

from corpusloader.controller import Controller
from corpusloader.view import ViewWrapperWidget, NotifierService

panel.extension(notifications=True)


class CorpusLoader(Viewer):
    """
    Public interface for the CorpusLoader module. Maintains a reference to the logic Controller and the GUI wrapper.
    A CorpusLoader object can be used as a Panel component, i.e. will render in a Panel GUI.
    The build_callback_fn will be called when the corpus is built (can be set using set_build_callback()).
    """
    def __init__(self, root_directory: str, **params):
        super().__init__(**params)
        self.controller: Controller = Controller(NotifierService(), root_directory)
        self.view: ViewWrapperWidget = ViewWrapperWidget(self.controller)

    def __panel__(self):
        return self.view

    def set_build_callback(self, callback: Callable, *args, **kwargs):
        """
        Allows a callback function to be set when the corpus has completed building
        :param callback: the function to call when the corpus has been built
        :param args: positional arguments to pass onto the callback function
        :param kwargs: keyword arguments to pass onto the callback function
        """
        self.controller.set_build_callback(callback, *args, **kwargs)

    def get_corpus(self) -> Optional[DataFrameCorpus]:
        """
        :return: the DataFrameCorpus object if it has been built, otherwise None.
        """
        return self.controller.get_corpus()
