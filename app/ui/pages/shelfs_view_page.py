import datetime as dt
import logging
import os
from app.utils import utils_funcs
from app.utils import my_exceptions

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys
from app.ui import qt_signals_handler
from app.utils import paths

def dynamic_pages_switching(func):

    def wrapper(self: ShelfsPagesWidget, page_index):

        if not self.pages_virtual_row[page_index]:
            self.new_page(self.shelfs_pages_data_handler.shelfs_pages_data[page_index])

        func(self, page_index)
        exceeding_pages = self.loaded_pages[self.max_loadable_pages_count:]

        if exceeding_pages:
            self.logger.info(f"Unloading {len(exceeding_pages)} shelfs page...")
            
            for exceeding_page in exceeding_pages:
                self.unload_page(exceeding_page)

    return wrapper

def dynamic_pages_loader(func):

    def wrapper(self: ShelfsPagesWidget):
        func(self, self.shelfs_pages_data_handler.shelfs_pages_data[:2])

    return wrapper

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
        self.search_le.textChanged.connect(self.exit_search)
        self.search_le.returnPressed.connect(lambda: self.search_shelfs(name=(self.search_le.text(), False)))

        #Shelfs pages widgets handler
        self.shelfs_pages_widget = ShelfsPagesWidget(self, self.books_handler, self.qt_signals_handler, self)

        #The pages numbers buttons at the bottom
        self.pages_numbers_widget = QtWidgets.QWidget()
        self.pages_numbers_widget.setObjectName("pages_numbers_widget")
        self.pages_numbers_lyt = QtWidgets.QGridLayout()
        self.pages_numbers_widget.setLayout(self.pages_numbers_lyt)
        
        self.page_selector_lb = QtWidgets.QLabel("Aller à : ")
        self.page_selector_le = QtWidgets.QLineEdit()
        self.page_selector_le.returnPressed.connect(lambda: self._jump_to_shelfs_page(self.page_selector_le.text()))
        
        self.pages_numbers_lyt.addWidget(self.page_selector_lb, 0, 8, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.pages_numbers_lyt.addWidget(self.page_selector_le, 0, 9, QtCore.Qt.AlignmentFlag.AlignCenter)

        #Adding widgets to main layout
        self.main_widget_lyt.addWidget(self.book_creation_b, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.shelf_creation_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_widget_lyt.addWidget(self.search_lb, 0, 1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.main_widget_lyt.addWidget(self.search_le, 0, 2, QtCore.Qt.AlignmentFlag.AlignRight)
        self.main_widget_lyt.addWidget(self.shelfs_pages_widget, 2, 0, 1, 3)
        self.main_widget_lyt.addWidget(self.pages_numbers_widget, 3, 0, 1, 3)
        self.main_lyt.addWidget(self.main_sa)
        self.pages_numbers_pb = []

        self.generate_shelfs_pages()
        
    @QtCore.Slot()
    def exit_search(self):
        
        if self.search_le.text() == "":
            self.shelfs_pages_widget.search_shelfs(list(self.books_handler.books_shelfs.values()), True)
            self.generate_shelfs_pages()
        
    def search_shelfs(self, **query):
        
        self.logger.debug(f"searching shelfs ({query=})...")

        try:
            result = self.books_handler.get_shelfs(**query)
            self.logger.debug(f"shelves search {result=}")
            
        except ValueError:
            self.logger.exception(f"Unable to get shelfs ! (query='{query}')")
            self.qt_signals_handler.notify_sg.emit("error", "", "", "")
            
        else:
            self.shelfs_pages_widget.search_shelfs(result)
            self.generate_shelfs_pages()

    def generate_shelfs_pages(self):
        
        #Destroying old widgets
        for button in self.pages_numbers_pb:
            self.pages_numbers_lyt.removeWidget(button)
            button.deleteLater()
            
        self.pages_numbers_pb.clear()
        self.shelfs_pages_widget.create_pages_from_data()

        #buttons for the five first shelfs pages
        for i in range(len(self.shelfs_pages_widget.pages_virtual_row[:5])):
            b = QtWidgets.QPushButton(str(i+1))
            b.clicked.connect(lambda qt_arg, page_index=i: self.shelfs_pages_widget.switch_current_page(page_index))
            self.pages_numbers_lyt.addWidget(b, 0, i, QtCore.Qt.AlignmentFlag.AlignCenter)
            self.pages_numbers_pb.append(b)
            
        #lb = QtWidgets.QLabel(". . .")
        #self.pages_numbers_lyt.addWidget(lb, 0, 6, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        #button for the last shelfs page
        
        if len(self.shelfs_pages_widget.pages_virtual_row) > 1:
            last_page_index = len(self.shelfs_pages_widget.pages_virtual_row) - 1
            b = QtWidgets.QPushButton(". . . "+str(last_page_index+1))
            b.setObjectName("last_page_b")
            b.clicked.connect(lambda qt_arg, page_index=last_page_index: self.shelfs_pages_widget.switch_current_page(page_index))
            self.pages_numbers_lyt.addWidget(b, 0, 7, QtCore.Qt.AlignmentFlag.AlignCenter)
            self.pages_numbers_pb.append(b)
        
    @QtCore.Slot(int)         
    def _jump_to_shelfs_page(self, page_index: int|str):
        
        if isinstance(page_index, str) and page_index.isdigit():
            page_index = int(page_index)
            
        else:
            self.qt_signals_handler.notify_sg.emit("error", "", "Cette page n'existe pas", "")
            return
            
        if isinstance(page_index, int) and page_index > 0 and page_index <= (len(self.shelfs_pages_widget.pages_virtual_row)):
            self.shelfs_pages_widget.switch_current_page(page_index-1)
            
        else:
            self.qt_signals_handler.notify_sg.emit("error", "", "Cette page n'existe pas", "")
        
    def _unload_empty_page(self, page_index):
        shelfs_page_widget = self.shelfs_pages_widget.pages_virtual_row[page_index]
        
        if shelfs_page_widget:
            self.shelfs_pages_widget.unload_page(shelfs_page_widget) 
            shelfs_page_widget.deleteLater()
            self.shelfs_pages_widget.shelfs_pages_data_handler.delete_data(page_index)
            self.generate_shelfs_pages()

class ShelfsPagesWidget(QtWidgets.QStackedWidget):

    def __init__(self, parent: QtWidgets.QWidget|None, books_handler: book_sys.BooksHandler, qt_signals_handler, shelfs_view_page: ShelfsViewPage):
        super().__init__(parent)

        #Assigning arguments to attr
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.shelfs_view_page = shelfs_view_page
        
        self.shelfs_by_pages_count = 10

        self.shelfs_pages_data_handler = ShelfsPagesDataHandler(self.books_handler, self.shelfs_by_pages_count)
        self.shelfs_pages_data_handler.setup_shelfs_pages()
        self.pages_virtual_row = [] #Used for making a virtual row representatio of the shelfs pages
        self.max_loadable_pages_count = 4
        self.loaded_pages = []

        #Setup logger
        self.logger = logging.getLogger(__name__+":ShelfsPagesWidgets")

        #Object name (for things like QSS stuff)
        self.setObjectName("shelfs_pages_widget")
        
        self.nothing_to_show_widget = QtWidgets.QWidget()
        self.nothing_to_show_widget_lyt = QtWidgets.QHBoxLayout()
        self.nothing_to_show_widget.setLayout(self.nothing_to_show_widget_lyt)
        self.nothing_to_show_lb = QtWidgets.QLabel(self)
        self.nothing_to_show_lb.setText("Votre recherche ne correpond à rien dans votre bibliothèque. Essayez avec un autre terme.")
        self.nothing_to_show_lb.setProperty("role", "nothing_to_show_lb")
        self.nothing_to_show_widget_lyt.addWidget(self.nothing_to_show_lb, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.addWidget(self.nothing_to_show_widget)

        self.prefill_virtual_row()     

    @dynamic_pages_switching
    def switch_current_page(self, page_index: int):
        page_obj = self.pages_virtual_row[page_index]

        if page_obj != self.currentWidget():
            self.setCurrentWidget(page_obj)
    
    def prefill_virtual_row(self):
        """
        Fill the <pages_virtual_row> attribute of None
        Please use it after use the <setup_shelfs_pages> method of the shelfs pages handler !
        """
        self.pages_virtual_row.clear()

        for i in range(len(self.shelfs_pages_data_handler.shelfs_pages_data)):
            self.pages_virtual_row.append(None)

    def new_page(self, page_data: list, skip_blank_pages=True):
        """
        Create a ShelfsPage object and add it to this widget
        """
        if not page_data[1:] and skip_blank_pages:
            return
        
        page_obj = self.create_page(page_data)
        self.add_page(page_obj)

    def create_page(self, page_data: list):
        """
        Create a new ShelfsPage object and return it
        """
        self.logger.debug(f"Creating shelves pages with index={page_data[:1]} shelves_count={len(page_data[1:])}")
        shelf_page = ShelfsPage(self, self.books_handler, self.qt_signals_handler, page_data[1:], page_data[0], self)
        return shelf_page

    def add_page(self, page_obj: ShelfsPage):
        """
        Add a ShelfsPage object to this widget
        """

        if page_obj in self.pages_virtual_row:

            if self.widget(page_obj.virtual_index) == self.pages_virtual_row[page_obj.virtual_index]:
                self.unload_page(page_obj)
                self.insertWidget(page_obj.virtual_index, page_obj)
                self.pages_virtual_row[page_obj.virtual_index] = page_obj
                self.loaded_pages.insert(0, page_obj)

            else:
                self.logger.error("the shelf page in the virtual row and the shelf page in the stacked widget are different !")

        else:
            self.pages_virtual_row[page_obj.virtual_index] = page_obj
            self.insertWidget(page_obj.virtual_index, page_obj)
            page_obj.widget_index = self.indexOf(page_obj) # type: ignore
            self.loaded_pages.insert(0, page_obj)
            
    def unload_page(self, page_obj: ShelfsPage):
        self.logger.debug(f"Unloading page, object={page_obj}, index={page_obj.virtual_index}")

        if page_obj in self.loaded_pages:
            self.removeWidget(page_obj)
            self.pages_virtual_row[page_obj.virtual_index] = None
            self.loaded_pages.remove(page_obj)
            page_obj.deleteLater()

        else:
            raise my_exceptions.ShelfPageNotLoadedError(page_obj)

    @dynamic_pages_loader
    def create_pages_from_data(self, pages_data: list|tuple|None=None):
        """
        Create and add ShelfsPage objects from a list|tuple of data

        Args:
        - pages_data (list|tuple): a list|tuple of pages data. the shelf pages handler
        - reset ()
        """

        if pages_data is None:
            pages_data = self.shelfs_pages_data_handler.shelfs_pages_data
            
        self.logger.debug(f"Generating shelfs pages widgets with {pages_data=}")

        for page_data in pages_data:
            self.new_page(page_data)
            
        if pages_data:
            self.switch_current_page(0)
            
    def delete_shelfs_page(self, shelfs_page:ShelfsPage):
        self.shelfs_view_page._unload_empty_page(shelfs_page.virtual_index)
        
    def search_shelfs(self, shelfs: list[book_sys.Shelf], include_default_shelf: bool=False):
        
        for page in self.loaded_pages:
            self.unload_page(page)
            
        self.loaded_pages.clear()            
        self.shelfs_pages_data_handler.setup_shelfs_pages(shelfs, include_default_shelf)
        self.prefill_virtual_row()
        
        if not shelfs:
            self.setCurrentWidget(self.nothing_to_show_widget)
            
class ShelfsPagesDataHandler:

    def __init__(self, books_handler: book_sys.BooksHandler, shelfs_by_pages_count: int):

        #Assigning arguments to attr
        self.books_handler = books_handler

        self.shelfs_by_pages_count = shelfs_by_pages_count
        self.shelfs_pages_data = []

    def setup_shelfs_pages(self, shelfs: list|None=None, include_default_shelf: bool=True):
        """
        Distribute the items from the shelves on different pages.
        
        - shelfs: An list of Shelfs objects. If not given or equal to None, then <books_handler.books_shelfs> is used.
        """
        
        if shelfs is None:
            shelfs = self.books_handler.books_shelfs.values() # type: ignore
            
        self.shelfs_pages_data.clear()
        shelfs_left = shelfs
        current_page_shelfs = [0, self.books_handler.default_shelf] if include_default_shelf else [0, ]

        for shelf_obj in shelfs_left: # type: ignore

            if len(current_page_shelfs[1:]) == self.shelfs_by_pages_count:
                self.shelfs_pages_data.append(current_page_shelfs.copy())
                current_page_shelfs = []
                current_page_shelfs.append(len(self.shelfs_pages_data))

            current_page_shelfs.append(shelf_obj)

        if current_page_shelfs[1:]:
            self.shelfs_pages_data.append(current_page_shelfs.copy())
            
    def delete_data(self, *indexes):
        
        for page_data in self.shelfs_pages_data:
            if page_data[0] in indexes:
                self.shelfs_pages_data.remove(page_data)
        
class ShelfsPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        shelfs_objs: list,
        virtual_index: int,
        shelfs_pages_widget: ShelfsPagesWidget,
    ):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.shelfs_objs = shelfs_objs
        self.shelfs_pages_widget = shelfs_pages_widget
        self.virtual_index = virtual_index
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

    def generate_shelfs_widgets(self, shelfs_objs: list|None=None, clear_lyt: bool=True):

        if shelfs_objs is None:
            shelfs_objs = self.shelfs_objs
            
        if clear_lyt:
            for shelf_widget in self.shelfs_widgets:
                self.main_layout.removeWidget(shelf_widget)
                shelf_widget.deleteLater()
    
        self.shelfs_widgets.clear()
        
        for shelf in shelfs_objs:
            
            if shelf == self.books_handler.default_shelf:
                shelf_widget = DefaultShelfWidget(                shelf, 
                    self.books_handler, 
                    self.qt_signals_handler,
                    self,
                )
                
            else:
                shelf_widget = ShelfWidget(
                    shelf, 
                    self.books_handler, 
                    self.qt_signals_handler,
                    self,
                )
                
            self.shelfs_widgets.append(shelf_widget)
            self.shelfs_container_layout.addWidget(
                shelf_widget, QtCore.Qt.AlignmentFlag.AlignTop
            )
            
    def delete_shelf_widget(self, shelf_widget: ShelfWidget):
        
        if shelf_widget in self.shelfs_widgets:
            self.logger.debug(f"Deleting shelf widget {shelf_widget} from shelfs page {self}")
            self.shelfs_objs.remove(shelf_widget.shelf)
            self.generate_shelfs_widgets()
            
            if not self.shelfs_widgets:
                self.shelfs_pages_widget.delete_shelfs_page(self)
                
        else:
            raise my_exceptions.ShelfWidgetNotFoundError(shelf_widget, self)
                

class ShelfWidget(QtWidgets.QWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        parent_page: ShelfsPage,
    ):
        super().__init__()
        self.icons_folder = paths.ICONS_PATH
        self.shelf = shelf
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.parent_page = parent_page
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
        
        try:
            self.parent_page.delete_shelf_widget(self)
            
        except my_exceptions.ShelfWidgetNotFoundError:
            self.logger.exception("Unable to delete shelf !")
            self.qt_signals_handler.notify_sg.emit("error", "", "", "")

class DefaultShelfWidget(ShelfWidget):
    def __init__(
        self,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        parent_virtual_index,
    ):
        super().__init__(shelf, books_handler, qt_signals_handler, parent_virtual_index)
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
