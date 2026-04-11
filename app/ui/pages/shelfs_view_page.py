import datetime as dt
import logging
import os
from app.utils import utils_funcs

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys
from app.ui import qt_signals_handler
from app.utils import paths

class ShelfsViewPage(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget|None, books_handler: book_sys.BooksHandler, qt_signals_handler: qt_signals_handler.QtSignalsHandler):
        super().__init__(parent)

        #Assingning arguments to attr
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler

        #Logger setup
        self.logger = logging.getLogger(__name__+":ShelfsViewPage")

        #Loading custom QSS
        utils_funcs.load_and_set_ss(
            os.path.join(paths.QSS_FILES_PATH, "shelfs_pages_view.qss"),
            os.path.join(paths.QSS_FILES_PATH, "general.qss"),
            widget=self, 
            logger=self.logger,
            )

        #Setting Main layout
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)

        #Setup a main scroll area
        self.main_widget = QtWidgets.QWidget()
        self.main_widget_lyt = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_widget_lyt)
        self.main_sa = QtWidgets.QScrollArea()
        self.main_sa.setWidget(self.main_widget)
        self.main_sa.setWidgetResizable(True)

        #Books and Shelfs creation buttons
        self.book_creation_b = QtWidgets.QPushButton("Nouveau livre")
        self.book_creation_b.clicked.connect(lambda: qt_signals_handler.switch_page_sg.emit("book_creation_page", True, {}))
        self.shelf_creation_b = QtWidgets.QPushButton("Nouvelle étagère")
        self.shelf_creation_b.clicked.connect(lambda: qt_signals_handler.switch_page_sg.emit("shelf_creation_page", True, {"mode":"creation"}))

        #Shelfs pages widgets handler
        self.shelfs_pages_widget = ShelfsPagesWidget(self, self.books_handler, self.qt_signals_handler)

        #The pages numbers buttons at the bottom
        self.pages_numbers_widget = QtWidgets.QWidget()
        self.pages_numbers_widget.setObjectName("pages_numbers_widget")
        self.pages_numbers_lyt = QtWidgets.QGridLayout()
        self.pages_numbers_widget.setLayout(self.pages_numbers_lyt)

        #Adding widgets to main layout
        self.main_widget_lyt.addWidget(self.book_creation_b, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.shelf_creation_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.shelfs_pages_widget, 2, 0)
        self.main_widget_lyt.addWidget(self.pages_numbers_widget, 3, 0)
        self.main_lyt.addWidget(self.main_sa)

        self.generate_shelfs_pages()

    def generate_shelfs_pages(self, reset_shelfs_data: bool=True):

        if reset_shelfs_data:
            self.shelfs_pages_widget.shelfs_pages_handler.setup_shelfs_pages()
            self.shelfs_pages_widget.prefill_virtual_row()
        self.shelfs_pages_widget.create_pages_from_data()

        for i in range(len(self.shelfs_pages_widget.pages_virtual_row)):
            b = QtWidgets.QPushButton(str(i+1))
            b.clicked.connect(lambda qt_arg, page_index=i: self.shelfs_pages_widget.switch_current_page(page_index))
            self.pages_numbers_lyt.addWidget(b, 0, i, QtCore.Qt.AlignmentFlag.AlignLeft)

class ShelfsPagesWidget(QtWidgets.QStackedWidget):

    def __init__(self, parent: QtWidgets.QWidget|None, books_handler: book_sys.BooksHandler, qt_signals_handler,):
        super().__init__(parent)

        #Assigning arguments to attr
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.shelfs_by_pages_count = 6

        self.shelfs_pages_handler = ShelfsPagesDataHandler(self.books_handler, self.shelfs_by_pages_count)
        self.shelfs_pages_handler.setup_shelfs_pages()
        self.pages_virtual_row = [] #Used for making a virtual row representatio of the shelfs pages

        #Setup logger
        self.logger = logging.getLogger(__name__+":ShelfsPagesWidgets")

        #Object name (for things like QSS stuff)
        self.setObjectName("shelfs_pages_widget")

        #Setup main layout
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)

        self.prefill_virtual_row()

    def switch_current_page(self, page_index: int):
        page_obj = self.pages_virtual_row[page_index]
        self.setCurrentWidget(page_obj)
    
    def prefill_virtual_row(self):
        """
        Fill the <pages_virtual_row> attribute of None
        Please use it after use the <setup_shelfs_pages> method of the shelfs pages handler !
        """
        self.pages_virtual_row.clear()

        for i in range(len(self.shelfs_pages_handler.shelfs_pages_data)):
            self.pages_virtual_row.append(None)

    def new_page(self, page_data: list|tuple):
        """
        Create a ShelfsPage object and add it to this widget
        """
        page_obj = self.create_page(page_data)
        self.add_page(page_obj)

    def create_page(self, page_data: list|tuple):
        """
        Create a new ShelfsPage object and return it
        """
        shelf_page = ShelfsPage(self, self.books_handler, self.qt_signals_handler, page_data[1:], page_data[0])
        return shelf_page

    def add_page(self, page_obj: ShelfsPage):
        """
        Add a ShelfsPage object to this widget
        """

        if self.pages_virtual_row[page_obj.virtual_index]:

            if self.widget(page_obj.virtual_index) == self.pages_virtual_row[page_obj.virtual_index]:
                self.removeWidget(self.pages_virtual_row[page_obj.virtual_index])
                self.insertWidget(page_obj.virtual_index, page_obj)
                self.pages_virtual_row[page_obj.virtual_index] = page_obj

            else:
                self.logger.error("the shelf page in the virtual row and the shelf page in the stacked widget are different !")

        else:
            self.pages_virtual_row[page_obj.virtual_index] = page_obj
            self.insertWidget(page_obj.virtual_index, page_obj)
            page_obj.widget_index = self.indexOf(page_obj) # type: ignore

    def create_pages_from_data(self, pages_data: list|tuple|None=None):
        """
        Create and add ShelfsPage objects from a list|tuple of data

        Args:
        - pages_data (list|tuple): a list|tuple of pages data. the shelf pages handler 
        """

        if not pages_data:
            pages_data = self.shelfs_pages_handler.shelfs_pages_data

        for page_data in pages_data:
            self.new_page(page_data)

class ShelfsPagesDataHandler:

    def __init__(self, books_handler: book_sys.BooksHandler, shelfs_by_pages_count: int):

        #Assigning arguments to attr
        self.books_handler = books_handler

        self.shelfs_by_pages_count = shelfs_by_pages_count
        self.shelfs_pages_data = []

    def setup_shelfs_pages(self):
        """
        Distribute the items from the shelves on different pages.
        """
        self.shelfs_pages_data.clear()
        shelfs_objs = self.books_handler.books_shelfs
        shelfs_left = list(shelfs_objs.values())
        current_page_shelfs = [0, self.books_handler.default_shelf]

        for shelf_obj in shelfs_left:

            if len(current_page_shelfs[1:]) == self.shelfs_by_pages_count:
                self.shelfs_pages_data.append(current_page_shelfs.copy())
                current_page_shelfs = []
                current_page_shelfs.append(len(self.shelfs_pages_data))

            current_page_shelfs.append(shelf_obj)

        if current_page_shelfs:
            self.shelfs_pages_data.append(current_page_shelfs.copy())
        
class ShelfsPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        shelfs_objs: tuple|list,
        index: int,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.shelfs_objs = shelfs_objs
        self.virtual_index = index
        self.widget_index = None

        self.setProperty("role", "shelfs_page")
        self.main_layout = QtWidgets.QGridLayout(self)

        self.shelfs_container = QtWidgets.QWidget(self)
        self.shelfs_container_layout = QtWidgets.QVBoxLayout(self.shelfs_container)
        self.shelfs_container.setLayout(self.shelfs_container_layout)
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.shelfs_container)

        self.main_layout.addWidget(self.scroll_area, 3, 0)

        #if self.index == 0:
        #    self.default_shelf_widget = DefaultShelfWidget(
        #        self.books_handler.default_shelf,
        #        self.books_handler,
        #        self.qt_signals_handler,
        #    )

        #    self.shelfs_container_layout.addWidget(
        #        self.default_shelf_widget, QtCore.Qt.AlignmentFlag.AlignTop
        #    )
        self.shelfs_widgets = []
        self.generate_shelfs_widgets(self.shelfs_objs)

    def generate_shelfs_widgets(self, shelfs_objs: tuple|list|None=None):

        if not shelfs_objs:
            shelfs_objs = self.shelfs_objs

        self.shelfs_widgets.clear()
        base_displayed_names = []

        for book_obj in self.books_handler.books.values():
            base_displayed_names.append(book_obj.title)
        
        for shelf in shelfs_objs:
            shelf_widget = ShelfWidget(
                shelf, self.books_handler, self.qt_signals_handler
            )
            base_displayed_names.append(shelf_widget.name_lb.text())
            #shelf_widget.name_lb.setText(utils_funcs.set_displayed_names(base_displayed_names)[from_index+i])
            self.shelfs_widgets.append(shelf_widget)
            self.shelfs_container_layout.addWidget(
                shelf_widget, QtCore.Qt.AlignmentFlag.AlignTop
            )

class ShelfWidget(QtWidgets.QWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__()
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


        self.name_lb = QtWidgets.QLabel(
            self.shelf.name
           if self.shelf.name
            else utils_funcs.unknown_shelf_name_fmt(self.shelf))
        
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
        self.books_handler.remove_shelf(self.shelf.id)
        self.qt_signals_handler.switch_page_sg.emit("shelfs_view_page", True, {})


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
