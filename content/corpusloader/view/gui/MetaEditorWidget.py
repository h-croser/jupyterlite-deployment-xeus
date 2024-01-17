from typing import Optional

from panel import Column, GridBox, bind, Row, Spacer
from panel.pane import Markdown, Str
from panel.widgets import Select, Checkbox

from corpusloader.controller import Controller
from corpusloader.controller.data_objects.CorpusHeader import CorpusHeader
from corpusloader.view.gui import AbstractWidget


class MetaEditorWidget(AbstractWidget):
    TABLE_BORDER_STYLE = {'border': '1px dashed black', 'border-radius': '5px'}
    ERROR_BORDER_STYLE = {'border': '1px solid red', 'border-radius': '5px'}
    HEADER_STYLE = {'margin-top': '0', 'margin-bottom': '0'}

    def __init__(self, view_handler: AbstractWidget, controller: Controller):
        super().__init__()
        self.view_handler: AbstractWidget = view_handler
        self.controller: Controller = controller

        self.corpus_table_container = GridBox(styles=MetaEditorWidget.TABLE_BORDER_STYLE)
        self.meta_table_container = GridBox(styles=MetaEditorWidget.TABLE_BORDER_STYLE)

        self.corpus_table_title = Markdown("## Corpus header editor")
        self.meta_table_title = Markdown("## Metadata header editor")

        self.text_header_dropdown = Select(name='Select document header', width=200)
        text_header_fn = bind(self._set_text_header, self.text_header_dropdown)

        self.link_row = Row(visible=False, styles=MetaEditorWidget.ERROR_BORDER_STYLE)
        self.corpus_link_dropdown = Select(name='Select corpus linking header', width=200)
        corpus_link_fn = bind(self._set_corpus_link_header, self.corpus_link_dropdown)
        self.meta_link_dropdown = Select(name='Select metadata linking header', width=200)
        meta_link_fn = bind(self._set_meta_link_header, self.meta_link_dropdown)
        link_emoji = '\U0001F517'
        self.link_markdown = Str(link_emoji, styles={"font-size": "2em", "margin": "auto"})
        self.link_row.objects = [self.corpus_link_dropdown,
                                 self.link_markdown,
                                 self.meta_link_dropdown,
                                 Column(corpus_link_fn, visible=False),
                                 Column(meta_link_fn, visible=False)]

        self.panel = Column(
            self.corpus_table_title,
            Row(self.text_header_dropdown, text_header_fn),
            self.corpus_table_container,
            self.meta_table_title,
            self.meta_table_container,
            Spacer(height=20),
            self.link_row
        )
        self.update_display()

    def update_display(self):
        self._build_corpus_table()
        self._build_meta_table()
        self._update_dropdowns()

    def _set_text_header(self, text_header_name: Optional[str]):
        self.controller.set_text_header(text_header_name)
        self.update_display()

    def _set_corpus_link_header(self, header_name: str):
        self.controller.set_corpus_link_header(header_name)
        self.update_display()

    def _set_meta_link_header(self, header_name: str):
        self.controller.set_meta_link_header(header_name)
        self.update_display()

    def _get_table_cells_list(self, headers: list[CorpusHeader], link_header: CorpusHeader, is_meta_table: bool) -> tuple[int, list]:
        all_datatypes: list[str] = self.controller.get_all_datatypes()
        text_header: Optional[CorpusHeader] = self.controller.get_text_header()

        table_cells: list = [Markdown('**Header name**', align='start'),
                             Markdown('**Datatype**', align='start'),
                             Markdown('**Include**', align='center')]
        if self.controller.is_meta_added():
            table_cells.append(Markdown('**Link**', align='center'))
        ncols: int = len(table_cells)

        for i, header in enumerate(headers):
            is_text = (header == text_header) and (not is_meta_table)
            is_link = (header == link_header)

            if is_link:
                header.include = True

            table_cells.append(Markdown(header.name, align='start', styles=MetaEditorWidget.HEADER_STYLE))

            datatype_selector = Select(options=all_datatypes, value=header.datatype.name, width=120, disabled=is_text)
            if is_meta_table:
                dtype_fn = bind(self.controller.update_meta_header, header, None, datatype_selector)
            else:
                dtype_fn = bind(self.controller.update_corpus_header, header, None, datatype_selector)
            table_cells.append(Row(datatype_selector, dtype_fn))

            include_checkbox = Checkbox(value=header.include, align='center', disabled=(is_text or is_link))
            if is_meta_table:
                include_fn = bind(self.controller.update_meta_header, header, include_checkbox, None)
            else:
                include_fn = bind(self.controller.update_corpus_header, header, include_checkbox, None)
            table_cells.append(Row(include_checkbox, include_fn))

            if self.controller.is_meta_added():
                if is_link:
                    link_identifier = self.link_markdown.clone()
                else:
                    link_identifier = ' '
                table_cells.append(link_identifier)

        return ncols, table_cells

    def _build_corpus_table(self):
        is_corpus_added = self.controller.is_corpus_added()
        self.corpus_table_title.visible = is_corpus_added
        self.corpus_table_container.visible = is_corpus_added

        corpus_headers: list[CorpusHeader] = self.controller.get_corpus_headers()
        link_header: Optional[CorpusHeader] = self.controller.get_corpus_link_header()

        ncols, corpus_table_cells = self._get_table_cells_list(corpus_headers, link_header, False)

        self.corpus_table_container.objects = corpus_table_cells
        self.corpus_table_container.ncols = ncols

    def _build_meta_table(self):
        is_meta_added = self.controller.is_meta_added()
        self.meta_table_title.visible = is_meta_added
        self.meta_table_container.visible = is_meta_added

        meta_headers: list[CorpusHeader] = self.controller.get_meta_headers()
        link_header: Optional[CorpusHeader] = self.controller.get_meta_link_header()

        ncols, meta_table_cells = self._get_table_cells_list(meta_headers, link_header, True)

        self.meta_table_container.objects = meta_table_cells
        self.meta_table_container.ncols = ncols

    def _update_dropdowns(self):
        is_meta_added = self.controller.is_meta_added()
        is_corpus_added = self.controller.is_corpus_added()
        self.link_row.visible = is_meta_added
        self.text_header_dropdown.visible = is_corpus_added

        corpus_headers: list[CorpusHeader] = self.controller.get_corpus_headers()
        meta_headers: list[CorpusHeader] = self.controller.get_meta_headers()
        text_header: Optional[CorpusHeader] = self.controller.get_text_header()
        corpus_link_header: Optional[CorpusHeader] = self.controller.get_corpus_link_header()
        meta_link_header: Optional[CorpusHeader] = self.controller.get_meta_link_header()

        self.text_header_dropdown.options = [h.name for h in corpus_headers]
        if text_header is not None:
            self.text_header_dropdown.value = text_header.name

        self.corpus_link_dropdown.options = [''] + [h.name for h in corpus_headers]
        if corpus_link_header is None:
            self.corpus_link_dropdown.value = ''
        else:
            self.corpus_link_dropdown.value = corpus_link_header.name

        self.meta_link_dropdown.options = [''] + [h.name for h in meta_headers]
        if meta_link_header is None:
            self.meta_link_dropdown.value = ''
        else:
            self.meta_link_dropdown.value = meta_link_header.name

        if (meta_link_header is None) or (corpus_link_header is None):
            self.link_row.styles = MetaEditorWidget.ERROR_BORDER_STYLE
        else:
            self.link_row.styles = {}
