import datetime as dt
import logging
import os
from app.utils import utils_funcs
from app.utils import my_exceptions

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys
from app.ui import qt_signals_handler
from app.ui import pages_view
from app.utils import paths

class ShelfsViewPage(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget|None, books_handler: book_sys.BooksHandler, qt_signals_handler: qt_signals_handler.QtSignalsHandler, settings_handler,):
        super().__init__(parent)

        #Assingning arguments to attr
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler

        #Logger setup
        self.logger = logging.getLogger(__name__+":ShelfsViewPage")

        #Loading custom QSS
        utils_funcs.load_and_set_ss(
            os.path.join(paths.QSS_FILES_PATH, "shelfs_view_page.qss"),
            os.path.join(paths.QSS_FILES_PATH, "general.qss"),
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
        self.book_creation_ico = QtGui.QIcon(os.path.join(paths.ICONS_PATH, "new_book_ico.png"))
        
        #Books and Shelfs creation buttons
        self.book_creation_b = QtWidgets.QPushButton("Nouveau livre")
        self.book_creation_b.clicked.connect(lambda: qt_signals_handler.switch_page_sg.emit("book_creation_page", True, {}))
        self.book_creation_b.setIcon(self.book_creation_ico)
        self.shelf_creation_b = QtWidgets.QPushButton("Nouvelle étagère")
        self.shelf_creation_b.clicked.connect(lambda: qt_signals_handler.switch_page_sg.emit("shelf_creation_page", True, {"mode":"creation"}))
        
        #Shelf research widgets
        self.search_lb = QtWidgets.QLabel("Rechercher : ")
        self.search_le = QtWidgets.QLineEdit()
        self.search_le.setClearButtonEnabled(True)
        # self.search_le.textChanged.connect(self.exit_search)
        # self.search_le.returnPressed.connect(lambda: self.search_shelfs(name=(self.search_le.text(), False)))

        #Shelfs pages widgets handler
        self.logger.debug(f"Assigning pages handler to self...")
        self.pages_view_handler = pages_view.PagesWidgetsHandler(self, self.qt_signals_handler, 5, 10, [])
        self.pages_view_handler.nothing_to_show_lb.setText("Il n'y a aucune étagère ici, pourquoi ne pas en créer une ?")

        #Adding widgets to main layout
        self.main_widget_lyt.addWidget(self.book_creation_b, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.shelf_creation_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.search_lb, 0, 1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.main_widget_lyt.addWidget(self.search_le, 0, 2, QtCore.Qt.AlignmentFlag.AlignRight)
        self.logger.debug(f"Adding pages handler to layout...")
        self.main_widget_lyt.addWidget(self.pages_view_handler, 3, 0, 1, 3)
        self.main_lyt.addWidget(self.main_sa)
        self.generate_shelfs_pages()
        
    # @QtCore.Slot()
    # def exit_search(self):
        
    #     if self.search_le.text() == "":
    #         self.shelfs_pages_widget.search_shelfs(list(self.books_handler.books_shelfs.values()), True)
    #         self.generate_shelfs_pages()
        
    # def search_shelfs(self, **query):
        
    #     self.logger.debug(f"searching shelfs ({query=})...")

    #     try:
    #         result = self.books_handler.get_shelfs(**query)
    #         self.logger.debug(f"shelves search {result=}")
            
    #     except ValueError:
    #         self.logger.exception(f"Unable to get shelfs ! (query='{query}')")
    #         self.qt_signals_handler.notify_sg.emit("error", "", "", "")
            
    #     else:
    #         self.shelfs_pages_widget.search_shelfs(result)
    #         self.generate_shelfs_pages()

    def create_shelves_widgets(self, shelves: list|tuple|None=None, include_default_shelf: bool=True):
        """
        Create shelfs widgets
        
        Args:
        - shelves: A sequence of shelf objects, if equal to None, the shelves object in the book handler will be used instead, default to None
        - include_default_shelf: Whether or not to create a shelf widget for the default book handler shel, default to True
        """
        
        shelves_values = shelves if shelves else self.books_handler.books_shelfs.values()
        
        self.shelves_widgets.clear()
        
        if include_default_shelf:
            self.shelves_widgets.append(DefaultShelfWidget(self.books_handler.default_shelf, self.books_handler, self.qt_signals_handler))
        
        self.logger.debug(f"Creating {len(shelves_values)+1 if include_default_shelf else len(shelves_values)} shelves widgets...")
        for shelf in shelves_values:
            shelf_widget = ShelfWidget(shelf, self.books_handler, self.qt_signals_handler)
            self.shelves_widgets.append(shelf_widget) 
            
            
    def generate_shelfs_pages(self):
        self.create_shelves_widgets()
        self.pages_view_handler.set_widgets(self.shelves_widgets)
        self.pages_view_handler.setup_pages_slices()
        self.pages_view_handler.generate_pages()
                
class ShelfWidget(pages_view.InPageWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(None, None)
        self.icons_folder = paths.ICONS_PATH
        self.shelf = shelf
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.logger = logging.getLogger(__name__)

        self.setProperty("role", "shelf_widget")
        self.main_layout = QtWidgets.QGridLayout(self)
        self.default_cover = os.path.join(
            paths.DEFAULT_COVERS_PATH, "default_shelf_cover.png"
        )

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
        #self.name_w = ShelfNameWidget(
        #    self, 
        #    self.shelf.name
        #    if self.shelf.name
        #    else utils_funcs.unknown_shelf_name_fmt(self.shelf))

        #self.name_w_sa.setWidget(self.name_w)
        self.total_books = QtWidgets.QLabel(f"{len(self.shelf.books_ids)} livres")
        self.total_books.setObjectName("total_books_lb")
        self.unread_books_count = 0
        self.on_reading_books_count = 0
        self.finished_books_count = 0

        for book_id in self.shelf.books_ids:
            book = self.books_handler.books[book_id]
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
        self.view_b = QtWidgets.QPushButton("Voir les livres")
        self.view_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "view_books_ico.png"))
        )
        self.view_b.setSizePolicy(self.button_size)
        self.view_b.clicked.connect(lambda: self.qt_signals_handler.switch_page_sg.emit("shelf_details_page", True, {"shelf":self.shelf}))

        self.edit_b = QtWidgets.QPushButton("Modifier")
        self.edit_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "edit_ico.png"))
        )
        self.edit_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "shelf_creation_page", True, {"mode": "edition", "shelf": self.shelf}
            )
        )
        self.edit_b.setSizePolicy(self.button_size)

        self.delete_b = QtWidgets.QPushButton("Supprimer")
        self.delete_b.setProperty("role", "delete_b")
        self.delete_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "cross_ico.png"))
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
        self.logger.debug(f"Attempting to delete shelf (ID={self.shelf.id})")
        self.books_handler.remove_shelf(self.shelf.id)
        
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
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(shelf, books_handler, qt_signals_handler)
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
