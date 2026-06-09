
import logging
import os
import shiboken6
from PySide6 import QtCore, QtGui, QtWidgets
import widgets_pagination_view

from app.src import book_sys
from app.ui import qt_signals_handler
from app.ui import my_widgets_pagination_view
from app.utils import utils_funcs
from app.utils import my_exceptions

class ShelfsViewPage(QtWidgets.QWidget):

    def __init__(
        self, 
        parent: QtWidgets.QWidget|None, 
        books_handler: book_sys.BooksHandler, 
        res_handler, qt_signals_handler: qt_signals_handler.QtSignalsHandler, 
        settings_handler,
        langs_handler,
        ):
        super().__init__(parent)

        #Assingning arguments to attr
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.variables_kw = {}

        #Logger setup
        self.logger = logging.getLogger(__name__+":ShelfsViewPage")

        #Loading custom QSS
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.shelfs_view_page"),
            self.res_handler.get_res("assets.qss.general"),
            widget=self, 
            logger=self.logger,
            )

        #Setting Main layout
        self.shelves_widgets = []
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)

        #Setup a main scroll area
        self.main_widget = QtWidgets.QWidget()
        self.main_widget_lyt = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_widget_lyt)
        self.main_sa = QtWidgets.QScrollArea()
        self.main_sa.setWidget(self.main_widget)
        self.main_sa.setWidgetResizable(True)
        
        #icons
        self.book_creation_ico = QtGui.QIcon(self.res_handler.get_res("assets.icons.new_book"))
        
        #Books and Shelfs creation buttons
        self.book_creation_b = QtWidgets.QPushButton(self.langs_handler.get_value("pages.shelfs_view_page.book_creation_b"))
        self.book_creation_b.clicked.connect(lambda: qt_signals_handler.switch_page_sg.emit("book_creation_page", True, {}))
        self.book_creation_b.setIcon(self.book_creation_ico)
        self.shelf_creation_b = QtWidgets.QPushButton(self.langs_handler.get_value("pages.shelfs_view_page.shelf_creation_b"))
        self.shelf_creation_b.clicked.connect(lambda: qt_signals_handler.switch_page_sg.emit("shelf_creation_page", True, {"mode":"creation"}))
        
        #Shelf research widgets
        self.search_result_widgets = []
        self.search_lb = QtWidgets.QLabel(self.langs_handler.get_value("research_lb"))
        self.search_le = QtWidgets.QLineEdit()
        self.search_le.setClearButtonEnabled(True)
        self.search_le.returnPressed.connect(lambda: self.search_shelfs(self.search_le.text()))
        self.search_le.textEdited.connect(self.exit_search)

        #Shelfs pages widgets handler
        self.pages_view_handler = my_widgets_pagination_view.MyWidgetsPaginationView(
            parent=self, 
            res_handler=res_handler,
            qt_signals_handler=self.qt_signals_handler,
            langs_handler=self.langs_handler, 
            max_loadables_pages_count=5, 
            widgets_by_page_count=10, 
            widgets=[],
            )

        #Adding widgets to main layout
        self.main_widget_lyt.addWidget(self.book_creation_b, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.shelf_creation_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.search_lb, 0, 1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.main_widget_lyt.addWidget(self.search_le, 0, 2, QtCore.Qt.AlignmentFlag.AlignRight)
        self.main_widget_lyt.addWidget(self.pages_view_handler, 3, 0, 1, 3)
        self.main_lyt.addWidget(self.main_sa)
        self.generate_shelves_pages()
        
    @QtCore.Slot(str)
    def search_shelfs(self, given_input: str):
        
        if given_input:
            self.qt_signals_handler.edit_progress_msg.emit(self.langs_handler.tr("research_in_progress_msg"))
            matches = self.books_handler.get_shelfs(name=(given_input, False, False))
            self.logger.info(f"Found {len(matches)} shelfs which matches with the query")
            
            if matches:
                self.search_result_widgets = self.create_shelves_widgets(matches, False)
                self.pages_view_handler.set_widgets(self.search_result_widgets.copy())
                
            else:
                self.pages_view_handler.set_widgets([])
                self.pages_view_handler.show_nothing_page()
            self.qt_signals_handler.edit_progress_msg.emit(" ")
            
    @QtCore.Slot()
    def exit_search(self):
        
        if not self.search_le.text():
            self.pages_view_handler.show_loading_page()
            
            for widget in self.shelves_widgets:
               if shiboken6.isValid(widget):
                    widget.deleteLater()
                
            self.shelves_widgets = self.create_shelves_widgets(list(self.books_handler.shelves.values()))
            self.pages_view_handler.set_widgets(self.shelves_widgets)
            
            for widget in self.search_result_widgets:
                widget.deleteLater()
                    
            self.search_result_widgets.clear()

    def create_shelves_widgets(self, shelves: list|tuple, include_default_shelf: bool=True):
        """
        Create shelves widgets with 'shelves' and return them
        
        Args:
        - shelves: A sequence of shelf objects, if equal to None, the shelves object in the book handler will be used instead, default to None
        - include_default_shelf: Whether or not to create a shelf widget for the default book handler shel, default to True
        """
        
        shelves_values = shelves
        
        shelves_widgets = []
        
        if include_default_shelf:
            shelves_widgets.append(
                DefaultShelfWidget(
                    self.books_handler.default_shelf, 
                    self.books_handler, 
                    self.res_handler, 
                    self.qt_signals_handler,
                    self.langs_handler,
                    )
                )
        
        self.logger.debug(f"Creating {len(shelves_values)+1 if include_default_shelf else len(shelves_values)} shelves widgets...")
        for shelf in shelves_values:
            shelf_widget = ShelfWidget(
                shelf, 
                self.books_handler, 
                self.res_handler, 
                self.qt_signals_handler,
                self.langs_handler
                )
            shelves_widgets.append(shelf_widget)
            
        return shelves_widgets
            
    def generate_shelves_pages(self):
        self.shelves_widgets = self.create_shelves_widgets(list(self.books_handler.shelves.values()))
        self.pages_view_handler.set_widgets(self.shelves_widgets.copy())
                
class ShelfWidget(widgets_pagination_view.InPageWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        res_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        langs_handler,
    ):
        super().__init__(None, None)
        self.shelf = shelf
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.qt_signals_handler = qt_signals_handler
        self.langs_handler = langs_handler
        self.logger = logging.getLogger(__name__)

        self.setProperty("role", "shelf_widget")
        self.main_layout = QtWidgets.QGridLayout(self)
        self.default_cover = self.res_handler.get_res("assets.defaults_covers.shelf")

        if self.shelf.cover_path:
            if os.path.exists(self.shelf.cover_path):
                self.displayed_cover = self.shelf.cover_path

            else:
                self.displayed_cover = self.default_cover
                self.logger.warning(f"Couldn't found shelf cover file at {self.shelf.cover_path}, switching to default cover")

        else:
            self.displayed_cover = self.default_cover


        self.name_lb = QtWidgets.QLabel(self.shelf.name + (f" ({self.shelf.name_suffix})" if self.shelf.name_suffix else ""))
        
        self.name_lb.setWordWrap(True)
        self.name_lb.setObjectName("name_lb")
        self.cover_pm = QtGui.QPixmap(self.displayed_cover)
        self.cover_lb = QtWidgets.QLabel()
        self.cover_lb.setPixmap(self.cover_pm)
        self.name_w_sa = QtWidgets.QScrollArea()
        self.name_w_sa.setWidgetResizable(True)
        self.total_books = QtWidgets.QLabel(f"{len(self.shelf._books)} livres")
        self.total_books.setObjectName("total_books_lb")
        self.unread_books_count = 0
        self.on_reading_books_count = 0
        self.finished_books_count = 0

        for book in self.shelf._books:
            if book.status == "unread":
                self.unread_books_count += 1

            elif book.status == "on_reading":
                self.on_reading_books_count += 1

            elif book.status == "finished":
                self.finished_books_count += 1

        self.unread_books_lb = QtWidgets.QLabel(f"{self.unread_books_count} non lus")
        self.on_reading_books_lb = QtWidgets.QLabel(
            f"{self.on_reading_books_count} en cours de lecture"
        )
        self.finished_books_lb = QtWidgets.QLabel(
            f"{self.finished_books_count} terminés"
        )
        self.unread_books_lb.setIndent(10)
        self.on_reading_books_lb.setIndent(10)
        self.finished_books_lb.setIndent(10)

        self.button_size = QtWidgets.QSizePolicy()
        self.view_b = QtWidgets.QPushButton(self.langs_handler.get_value("pages.shelfs_view_page.view_b"))
        self.view_b.setIcon(
            QtGui.QIcon(self.res_handler.get_res("assets.icons.view_books"))
        )
        self.view_b.setSizePolicy(self.button_size)
        self.view_b.clicked.connect(lambda: self.qt_signals_handler.switch_page_sg.emit("shelf_details_page", True, {"shelf":self.shelf}))

        self.edit_b = QtWidgets.QPushButton(self.langs_handler.get_value("edit_b"))
        self.edit_b.setIcon(
            QtGui.QIcon(self.res_handler.get_res("assets.icons.edit"))
        )
        self.edit_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "shelf_creation_page", True, {"mode": "edition", "shelf": self.shelf}
            )
        )
        self.edit_b.setSizePolicy(self.button_size)

        self.delete_b = QtWidgets.QPushButton(self.langs_handler.get_value("delete_b"))
        self.delete_b.setProperty("role", "delete_b")
        self.delete_b.setIcon(
            QtGui.QIcon(self.res_handler.get_res("assets.icons.exit"))
        )
        self.delete_b.setSizePolicy(self.button_size)
        self.delete_b.clicked.connect(self.delete_shelf)

        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.name_lb, 0, 0, 1, 2)
        self.main_layout.addWidget(self.cover_lb, 1, 0, 8, 1)
        self.main_layout.addWidget(self.total_books, 1, 1)
        self.main_layout.addWidget(self.unread_books_lb, 2, 1)
        self.main_layout.addWidget(self.on_reading_books_lb, 3, 1)
        self.main_layout.addWidget(self.finished_books_lb, 4, 1)
        self.main_layout.addWidget(self.view_b, 5, 1)
        self.main_layout.addWidget(self.edit_b, 6, 1)
        self.main_layout.addWidget(self.delete_b, 7, 1)

        # The book creation information

    def delete_shelf(self):
        self.logger.debug(f"Attempting to delete shelf (ID={self.shelf.id})...")
        self.books_handler.delete_shelf(self.shelf.id)
        
        if self.pages_widgets_handler:
        
            try:
                self.pages_widgets_handler.delete_widget(self)
                
            except my_exceptions.InvalidWidgetIndexError:
                self.logger.exception("Unable to delete shelf !")
                self.qt_signals_handler.notify_sg.emit("error", "", "", "")
                
        else:
            self.logger.error(f"Unable to delete a shelf widget with ShelfID={self.shelf.id}: No valid parent page found !")

class DefaultShelfWidget(ShelfWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        res_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        langs_handler,
    ):
        super().__init__(
            shelf, 
            books_handler, 
            res_handler, 
            qt_signals_handler,
            langs_handler,
            )
        self.edit_b.hide()
        self.delete_b.hide()
        self.main_layout.removeWidget(self.cover_lb)
        self.main_layout.addWidget(self.cover_lb, 1, 0, 6, 1)

class ShelfNameWidget(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget|None, label_text: str, label_name: str="name_lb"):
        super().__init__(parent)

        self.main_lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_lyt)
        self.label = QtWidgets.QLabel(label_text)
        self.label.setObjectName(label_name)
        self.main_lyt.addWidget(self.label)
