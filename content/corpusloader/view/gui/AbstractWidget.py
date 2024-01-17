from abc import ABC, abstractmethod
from typing import Callable

from panel import Row, Column
from panel.layout import Panel
from panel.widgets import Button


class AbstractWidget(ABC):
    """
    An abstract class for Panel GUI widgets. Provides methods to set widget visibility and update the display of all
    child widgets.
    """
    def __init__(self):
        self.panel: Panel = Row()
        self.children: list[AbstractWidget] = []

    def __panel__(self) -> Panel:
        return self.panel

    def update_displays(self):
        self.update_display()
        for child in self.children:
            child.update_displays()

    def get_visibility(self) -> bool:
        return self.panel.visible

    def set_visibility(self, is_visible: bool):
        self.panel.visible = is_visible

    def toggle_visibility(self):
        self.panel.visible = not self.panel.visible

    def create_confirmation_box(self, *_, confirm_callable: Callable):
        def confirm_action(_):
            confirm_callable()
            response.clear()

        def cancel_action(_):
            response.clear()

        confirmation = Button(name='Confirm')
        confirmation.on_click(confirm_action)
        cancel = Button(name='Cancel')
        cancel.on_click(cancel_action)

        response = Column("Are you sure?", Row(confirmation, cancel))
        response.show()

    @abstractmethod
    def update_display(self):
        raise NotImplementedError()
