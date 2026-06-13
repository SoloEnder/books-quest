import logging
from typing import Sequence

from PySide6 import QtCore, QtWidgets, QtGui

from app.src import book_sys
from app.ui import qt_signals_handler
from app.ui.main_pages import book_creation_page, shelf_creation_page, shelf_details_page, shelfs_view_page
from app.ui import notification_service
from app.utils import utils_funcs
from app.src import json_dicts_paths_handler

class UI(QtWidgets.QMainWindow):
    def __init__(self, books_handler, res_handler, settings_handler: json_dicts_paths_handler.JSONDictPathHandler, langs_handler: json_dicts_paths_handler.JSONDictPathHandler):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler

        self.qt_signals_handler = qt_signals_handler.QtSignalsHandler()
        self.notification_service = notification_service.NotificationService(
            self, 
            self.langs_handler
            )
        self.qt_signals_handler.notify_sg.connect(self.notification_service.notify)
        self.my_stacked_widgets = MyStackedWidgets(
            self, self.books_handler, self.res_handler, self.qt_signals_handler, self.settings_handler, self.langs_handler,
        )
        self.toolbar = ToolBar(self, self.res_handler, self.langs_handler)
        self.addToolBar(self.toolbar)
        self.toolbar.close_page_act.triggered.connect(lambda: self.my_stacked_widgets.close_page())
        self.qt_signals_handler.add_action_sg.connect(self.toolbar.addActions)
        self.gen_qss_filepath = self.res_handler.get_res("assets.qss.general")
        utils_funcs.load_and_set_ss(self.gen_qss_filepath, widget=self.my_stacked_widgets, logger=self.logger)
        self.my_stacked_widgets.switch_page("shelfs_view_page")
        self.setCentralWidget(self.my_stacked_widgets)
        self.setWindowTitle("Books Quest")
        self.setWindowIcon(QtGui.QIcon(self.res_handler.get_res("assets.splashscreen.splashscreen")))
        self.progress_info_lb = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.progress_info_lb)
        self.qt_signals_handler.edit_progress_msg.connect(self.set_progress_msg)
        
    def set_progress_msg(self, msg: str):
        self.progress_info_lb.setText(msg)
        QtWidgets.QApplication.processEvents()

    def show_indev_warn(self):
        """
        Show the in develepoment warning window
        """
        
        #self.indev_warning_w.show()
        QtWidgets.QMessageBox.information(self, "Indev Warning", "This program is in developement ! If you see any bug, please report it <a href='https://github.com/SoloEnder/books-quest/issues'>here</a>")

class MyStackedWidgets(QtWidgets.QStackedWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_sys.BooksHandler,
        res_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler,
        langs_handler,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.redundant_lang_path = ""
        self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
            self, 
            self.books_handler, 
            res_handler, 
            self.qt_signals_handler, 
            self.settings_handler, 
            self.langs_handler
        )
        self.shelf_details_page = shelf_details_page.ShelfDetailsPage(self, 
            self.books_handler.default_shelf, 
            self.books_handler, 
            self.res_handler, 
            self.qt_signals_handler, 
            self.settings_handler,
            self.langs_handler,
            )
        self.book_creation_page = book_creation_page.BookCreationPage(
            self,
            self.books_handler,
            self.res_handler,
            self.qt_signals_handler,
            self.settings_handler,
            self.langs_handler,
        )
        self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
            self, 
            self.books_handler, 
            self.res_handler, 
            self.qt_signals_handler, 
            self.settings_handler,
            self.langs_handler,
            mode="creation",
        )
        self.pages = {
            "SHELFS_VIEW_PAGE": self.shelfs_view_page,
            "SHELF_DETAILS_PAGE": self.shelf_details_page,
            "BOOK_CREATION_PAGE": self.book_creation_page,
            "SHELF_CREATION_PAGE": self.shelf_creation_page,
        }
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.book_creation_page)
        self.addWidget(self.shelfs_view_page)
        self.addWidget(self.shelf_creation_page)
        self.history = []
        self.switch_page("SHELFS_VIEW_PAGE")
        self.qt_signals_handler.switch_page_sg.connect(self.switch_page)
        self.qt_signals_handler.close_page_sg.connect(self.close_page)

    @QtCore.Slot(str, bool, dict)
    def switch_page(self, page_name: str, refresh: bool = False, page_args={}):
        """
        Change the current widget displayed by the value of <name> in the attribute <pages>

        Args:
            - page_name (str): the name of the page, a key of the attribute <pages>.
            - refresh (bool): if true, the page will be refreshed. default to False
        """
        
        self.logger.info(f"Switching to page {page_name}...")
        if page_name in self.pages.keys():
            self.qt_signals_handler.edit_progress_msg.emit(self.langs_handler.get_value("shared.progress.loading_page"))
            if refresh:
                self.refresh(page_name, page_args)

            page_obj = self.pages[page_name]
            self.setCurrentWidget(page_obj)

            self.history.insert(0, page_name)
            self.qt_signals_handler.edit_progress_msg.emit(" ")

        else:
            self.logger.error(f"Page <{page_name}> not found !")

    @QtCore.Slot(bool)
    def close_page(self):
        
        if len(self.history) > 1:
            self.switch_page(
                self.history[1],
                True,
                self.pages[self.history[1]].variables_kw
            )
            del self.history[1]
            del self.history[0]
        
        # history_copy = self.history.copy()
        # if len(history_copy) >= 1:
            
        #     if history_copy[0] != history_copy[1]:
        #         del self.history[1]
        #         self.switch_page(
        #             history_copy[1],
        #             True if refresh else False,
        #             self.pages[history_copy[1]].variables_kw
        #         )

    def refresh(self, page_name, page_args):
        self.logger.debug(f"Pages switch history={self.history}")
        self.logger.debug(f"Refreshing {page_name} with kwargs {page_args}")
        if page_name == "SHELFS_VIEW_PAGE":
            self.removeWidget(self.shelfs_view_page)
            self.shelfs_view_page.setParent(None)
            self.shelfs_view_page.deleteLater()
            self.shelfs_view_page = shelfs_view_page.ShelfsViewPage(
                self,
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.settings_handler,
                self.langs_handler,
            )
            self.pages["SHELFS_VIEW_PAGE"] = self.shelfs_view_page
            self.addWidget(self.shelfs_view_page)

        elif page_name == "BOOK_CREATION_PAGE":
            self.removeWidget(self.book_creation_page)
            self.book_creation_page.setParent(None)
            self.book_creation_page.deleteLater()
            self.book_creation_page = book_creation_page.BookCreationPage(
                self, 
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler, 
                self.settings_handler,
                self.langs_handler,
            )
            self.pages["BOOK_CREATION_PAGE"] = self.book_creation_page
            self.addWidget(self.book_creation_page)

        elif page_name == "SHELF_CREATION_PAGE":
            self.removeWidget(self.shelf_creation_page)
            self.shelf_creation_page.setParent(None)
            self.shelf_creation_page.deleteLater()
            self.shelf_creation_page = shelf_creation_page.ShelfCreationPage(
                self, 
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler, 
                self.settings_handler,
                self.langs_handler,
                **page_args,
            )
            self.pages["SHELF_CREATION_PAGE"] = self.shelf_creation_page
            self.addWidget(self.shelf_creation_page)

        elif page_name == "SHELF_DETAILS_PAGE":
            self.removeWidget(self.shelf_details_page)
            self.shelf_details_page.setParent(None)
            self.shelf_details_page.deleteLater()
            self.shelf_details_page = shelf_details_page.ShelfDetailsPage(
                self, 
                page_args["shelf"], 
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.settings_handler,
                self.langs_handler,
                )
            self.pages["SHELF_DETAILS_PAGE"] = self.shelf_details_page
            self.addWidget(self.shelf_details_page)
            
        else:
            raise ValueError(f"Unknown page : '{page_name}'")
            
    def my_tr(self, lang_path: str, fill: bool=True, **kwargs) -> str:
        """Do the same as the 'langs_handler.tr()' attribute, but auto-complete the first part of the 'lang_path' by the value of the 'rebondant_lang_path' attr.\n
        Note that your shortcut lang_path must start by '.' for the auto completion to work.
        
        Parameters
        ----------
        fill (bool=True): specifies wheter or not to fill the begining of the lang_path
        **kwargs: the additionnal arguments for the translation text
        
        Returns
        -------
        str: the translation
        
        Example:
        --------
        you can pass the lang_path '.buttons.do_something' instead of 'main_pages.page_name.buttons.do_something'\n
        if the value of the 'redundant_lang_path' is 'main_pages.page_name'
        """
        
        if fill and hasattr(self, "redundant_lang_path") and lang_path.startswith("."):
            return self.langs_handler.tr(self.redundant_lang_path+lang_path, **kwargs)
        
        else:
            return self.langs_handler.tr(lang_path, **kwargs)

class IndevWarnWidget(QtWidgets.QMessageBox):

    def __init__(self, parent: QtWidgets.QWidget|None):
        super().__init__(parent)

        #Setting window title
        self.setWindowTitle("Indev Warning")

        #Setting text
        self.setText("This program is in developement ! If you see any bug which is not already reported, please report it <a href='https://github.com/SoloEnder/books-quest/issues'>here</a>")
    
class ToolBar(QtWidgets.QToolBar):
    
    def __init__(self, parent: QtWidgets.QWidget|None, res_handler, langs_handler):
        super().__init__(parent)
        self.res_handler = res_handler
        self.langs_handler = langs_handler
        self.redundant_lang_path = "toolbar"
        
        self.close_page_act = QtGui.QAction(self.my_tr(".actions.close_page"))
        self.close_page_act.setIcon(QtGui.QIcon(self.res_handler.get_res("assets.icons.exit")))
        self.addAction(self.close_page_act)
        
    def my_tr(self, lang_path: str, fill: bool=True, **kwargs) -> str:
        """Do the same as the 'langs_handler.tr()' attribute, but auto-complete the first part of the 'lang_path' by the value of the 'rebondant_lang_path' attr.\n
        Note that your shortcut lang_path must start by '.' for the auto completion to work.
        
        Parameters
        ----------
        fill (bool=True): specifies wheter or not to fill the begining of the lang_path
        **kwargs: the additionnal arguments for the translation text
        
        Returns
        -------
        str: the translation
        
        Example:
        --------
        you can pass the lang_path '.buttons.do_something' instead of 'main_pages.page_name.buttons.do_something'\n
        if the value of the 'redundant_lang_path' is 'main_pages.page_name'
        """
        
        if fill and hasattr(self, "redundant_lang_path") and lang_path.startswith("."):
            return self.langs_handler.tr(self.redundant_lang_path+lang_path, **kwargs)
        
        else:
            return self.langs_handler.tr(lang_path, **kwargs)
