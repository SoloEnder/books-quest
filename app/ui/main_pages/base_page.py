from PySide6 import QtGui, QtWidgets

from app.src import langs_handler, resources_handler, settings_handler
from app.ui import qt_signals_handler


class BasePage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        res_handler: resources_handler.RessourcesHandler,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        """
        This class is the base skellet of all pages, it define a main layout, and a main widgets with a scroll are\n
        If you want to add some widget, you should only deal with the  'main_widget' and the 'main_lyt' widgets.
        """
        # Assigning arguments
        self.res_handler = res_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.qt_signals_handler = qt_signals_handler
        self.PAGE_NAME = "BASE_PAGE"  # the page name, mostly used for identify the page on page switching
        # Calling the __init__ of the parent
        super().__init__(parent)
        self.base_main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.base_main_lyt)

        # The main widget (where all the true widgets are) and its scroll area
        self.main_widget = QtWidgets.QWidget(self)
        self.main_lyt = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_lyt)
        self.base_main_lyt.addWidget(self.main_widget)
        self.main_scrollarea = QtWidgets.QScrollArea()
        self.main_scrollarea.setWidgetResizable(True)
        self.main_scrollarea.setWidget(self.main_widget)
        self.base_main_lyt.addWidget(self.main_scrollarea, 0, 0)

    def move_main_widget(
        self,
        new_row: int,
        new_column: int,
        alignment: QtGui.Qt.AlignmentFlag | None = None,
    ):
        """
        Moves the main_widget place in the base_main_lyt\n
        This method is usefull if you want to place other widgets before the main_widget placement.

        Parameters
        ----------
        new_row (int): the row where main_widget will be moved
        new_column (int): the column where main_widget will be moved
        alignment (PySide6.QtGui.Qt.AlignmentFlag|None=None): specifies the alignment of main_widget, default to None.
        """
        self.base_main_lyt.removeWidget(self.main_scrollarea)

        if alignment:
            self.base_main_lyt.addWidget(
                self.main_scrollarea, new_row, new_column, alignment
            )

        else:
            self.base_main_lyt.addWidget(self.main_scrollarea, new_row, new_column)
