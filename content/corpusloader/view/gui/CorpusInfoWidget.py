from typing import Optional

from panel import Column, Row
from panel.pane import Markdown

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget


class CorpusInfoWidget(AbstractWidget):
    def __init__(self, controller: Controller):
        super().__init__()
        self.controller: Controller = controller

        self.panel = Column(Markdown("**No corpus loaded**"))

    @staticmethod
    def _build_header_markdown_table(headers: list[str], dtypes: list[str]) -> Markdown:
        if len(headers) != len(dtypes):
            return Markdown(" ")

        title = "**Header data types**"
        header_row = "| " + " | ".join(headers)
        spacer_row = "| :-: " * len(headers) + "|"
        data_row = "| " + " | ".join(dtypes)

        header_table_text = f"{title}\n{header_row}\n{spacer_row}\n{data_row}"
        return Markdown(header_table_text)

    def update_display(self):
        corpus_info: Optional[dict] = self.controller.get_corpus_info()
        if corpus_info is None:
            self.panel.objects = [Markdown("**No corpus loaded**")]
            return

        name: str = corpus_info.get('name')
        num_rows: str = corpus_info.get('rows')
        num_files: str = corpus_info.get('files')
        headers: list[str] = corpus_info.get('headers')
        dtypes: list[str] = corpus_info.get('dtypes')

        row_info: str = f"**{num_rows}** document row"
        if num_rows != '1':
            row_info += 's'
        file_info: str = f"**{num_files}** source file"
        if num_files != '1':
            file_info += 's'

        header_table = CorpusInfoWidget._build_header_markdown_table(headers, dtypes)
        corpus_info_ls: list = [Markdown(f"## {name} Overview"),
                                Row(Markdown(row_info),
                                    Markdown(file_info)),
                                header_table]

        self.panel.objects = corpus_info_ls
