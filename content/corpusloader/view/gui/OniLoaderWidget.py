from panel import Row

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget


class OniLoaderWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.panel = Row()

    def update_display(self):
        pass
