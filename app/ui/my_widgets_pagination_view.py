import logging

import widgets_pagination_view
from PySide6 import QtGui, QtWidgets

from app.src import langs_handler, resources_handler
from app.ui import qt_signals_handler
from app.utils import utils_funcs


class MyWidgetsPaginationView(widgets_pagination_view.WidgetsPaginationView):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        res_handler: resources_handler.RessourcesHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        langs_handler: langs_handler.LangsHandler,
        max_loadables_pages_count: int,
        widgets_by_page_count: int,
        widgets: widgets_pagination_view.InPageWidgetsList,
        **config,
    ):
        self.init_completed = False
        super().__init__(
            parent=parent,
            max_loadables_pages_count=max_loadables_pages_count,
            widgets_by_page_count=widgets_by_page_count,
            widgets=widgets,
            **config,
        )
        self.logger = logging.getLogger(__name__ + "WidgetsPaginationView")
        self.res_handler = res_handler
        self.langs_handler = langs_handler
        self.qt_qignals_handler = qt_signals_handler
        self.redundant_lang_path = "my_widgets_pagination_view"
        self.jump_to_page_lb.setText(self.langs_handler.tr("shared.actions.go_to"))
        self.nothing_to_show_page = NothingToShowPage(
            self, self.langs_handler.tr("shared.msg.nothing_to_show")
        )
        self.main_lyt.addWidget(self.nothing_to_show_page, 0, 0)
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.widgets_pagination_view"),
            widget=self,
            logger=self.logger,
        )
        self.init_completed = True

    def generate_pages(self):
        super().generate_pages()

        if self.init_completed:
            if self.widgets:
                self.nothing_to_show_page.setVisible(False)

            else:
                self.nothing_to_show_page.setVisible(True)

    def delete_widget(self, widget: widgets_pagination_view.InPageWidget):
        super().delete_widget(widget)
        if self.widgets:
            self.nothing_to_show_page.setVisible(False)

        else:
            self.nothing_to_show_page.setVisible(True)

    def _generate_pages_buttons(self, pages_indexes: list | tuple):
        super()._generate_pages_buttons(pages_indexes)

        if len(self.pages_numbers_lyt_widgets) > 1:
            last_button = self.pages_numbers_lyt_widgets[-1]
            last_button.setText(f". . . {last_button.text()}")
            last_button.setObjectName("last_page_b")

    def _jump_to_page(self, given_input):

        try:
            super()._jump_to_page(given_input)

        except ValueError:
            self.qt_qignals_handler.notify_sg.emit(
                "error",
                "Page not found",
                self.tr("my_widgets_pagination_view.notifications.invalid_page_index"),
                "",
            )


class NothingToShowPage(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None, text):
        super().__init__(parent)
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)
        self.label = QtWidgets.QLabel(text)
        self.label.setProperty("role", "nothing_to_show_lb")
        self.main_lyt.addWidget(self.label, 0, 0, QtGui.Qt.AlignmentFlag.AlignCenter)

    def edit_label_text(self, new_text: str):
        self.label.setText(new_text)
