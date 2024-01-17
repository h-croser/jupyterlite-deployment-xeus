from panel import Row, Spacer, Column, HSpacer
from panel.pane import Markdown
from panel.widgets import Button, TextInput

from corpusloader.controller import Controller
from corpusloader.controller.data_objects import FileReference
from corpusloader.view import ViewWrapperWidget
from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.FileSelectorWidget import FileSelectorWidget
from corpusloader.view.gui.MetaEditorWidget import MetaEditorWidget


class FileLoaderWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapperWidget, controller: Controller):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler
        self.controller: Controller = controller
        
        self.load_as_corpus_button: Button = Button(name='Load as corpus', width=130,
                                                    button_style='outline', button_type='success')
        self.load_as_corpus_button.on_click(self.load_as_corpus)
        self.load_as_meta_button: Button = Button(name='Load as metadata', width=130,
                                                  button_style='outline', button_type='success')
        self.load_as_meta_button.on_click(self.load_as_meta)

        self.unload_all_button: Button = Button(name="Unload all", width=100, button_style='solid',
                                                button_type='danger', disabled=True)
        self.unload_all_button.on_click(self.unload_all)
        self.unload_selected_button: Button = Button(name="Unload selected", width=100, button_style='outline',
                                                     button_type='danger', disabled=True)
        self.unload_selected_button.on_click(self.unload_selected)

        self.loaded_file_info = Markdown()
        
        self.corpus_name_input = TextInput(placeholder='Corpus name', width=150, visible=False)
        self.build_button = Button(name='Build corpus', button_style='solid', button_type='success', visible=False)
        self.build_button.on_click(self.build_corpus)

        self.file_selector = FileSelectorWidget(view_handler, controller)
        self.meta_editor = MetaEditorWidget(view_handler, controller)

        self.panel = Row(
            Column(
                self.file_selector,
                Row(Column(
                    Row(self.load_as_corpus_button,
                        self.load_as_meta_button),
                    Row(self.corpus_name_input,
                        self.build_button)
                ),
                    self.loaded_file_info,
                    HSpacer(),
                    self.unload_selected_button,
                    self.unload_all_button,
                    width=700)
            ),
            Spacer(width=50),
            self.meta_editor)
        self.children = [self.file_selector, self.meta_editor]
        self.update_display()

    def update_display(self):
        files_added: bool = self.controller.is_meta_added() or self.controller.is_corpus_added()
        self._set_build_buttons_status(files_added)
        self.loaded_file_info.object = self.get_loaded_file_info()

    def get_loaded_file_info(self) -> str:
        file_counts: dict[str, int] = self.controller.get_loaded_file_counts()
        count_str: str = ""
        for filetype in file_counts:
            count_str += f"{filetype}: {file_counts[filetype]}\n"

        return count_str

    def _set_build_buttons_status(self, active: bool, *_):
        if active:
            self.corpus_name_input.visible = True
            self.build_button.visible = True
            self.unload_all_button.disabled = False
            self.unload_selected_button.disabled = False
        else:
            self.corpus_name_input.visible = False
            self.build_button.visible = False
            self.unload_all_button.disabled = True
            self.unload_selected_button.disabled = True

    def load_as_corpus(self, *_):
        file_ls: list[FileReference] = self.file_selector.get_selector_value()
        self.view_handler.load_corpus_from_filepaths(file_ls)

    def load_as_meta(self, *_):
        file_ls: list[FileReference] = self.file_selector.get_selector_value()
        self.view_handler.load_meta_from_filepaths(file_ls)

    def unload_selected(self, *_):
        file_ls: list[FileReference] = self.file_selector.get_selector_value()
        self.controller.unload_filepaths(file_ls)
        self.view_handler.update_displays()

    def unload_all(self, *_):
        self.controller.unload_all()
        self.view_handler.update_displays()

    def build_corpus(self, *_):
        self.view_handler.build_corpus(self.corpus_name_input.value)
