
import os
import logging
from PySide6 import QtWidgets, QtCore, QtGui

from app.src import resources_handler as res_handler
from app.utils import my_exceptions
from app.src import langs_handler
from app.src import book_sys
from app.ui import qt_signals_handler
from app.ui import widgets_pages_view
from app.utils import utils_funcs



class ShelfDetailsPage(QtWidgets.QWidget):

    def __init__(
        self, 
        parent: QtWidgets.QWidget|None, 
        shelf: book_sys.Shelf, 
        books_handler: book_sys.BooksHandler,
        res_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler,
        langs_handler,
        ):
        
        super().__init__(parent)
        self.shelf = shelf
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.variables_kw = {"shelf":self.shelf}

        #logger
        self.logger = logging.getLogger(__name__)
        
        self.lang_data = self.langs_handler.get_value("pages.shelf_details_page")
        #Widgets
        self.gen_qss_filepath = self.res_handler.get_res("assets.qss.general")
        self.page_qss_filepath = self.res_handler.get_res("assets.qss.shelf_details_page")
        utils_funcs.load_and_set_ss(self.gen_qss_filepath, self.page_qss_filepath, widget=self, logger=self.logger)
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)
        self.main_widget = QtWidgets.QWidget()
        self.books_widgets = []

        self.nothing_to_show_lb = QtWidgets.QLabel(self.langs_handler.get_value("nothing_to_show_lb"))
        self.nothing_to_show_lb.setProperty("role", "nothing_to_show_lb")
        self.nothing_to_show_lb.hide()

        #widgets pages view handler
        self.widgets_pages_view_handler = widgets_pages_view.PagesWidgetsHandler(
            self,
            self.res_handler,
            self.qt_signals_handler,
            self.langs_handler,
            5,
            10,
            [],
        )

        #books widgets
        self.generate_books_pages()

        #Adding widgets to layout
        self.main_lyt.addWidget(self.widgets_pages_view_handler, 0, 0)

    def create_books_widgets(self, books: book_sys.BooksList):
        """
        Generate widget ('BookWidget') for every book ('book_sys.Book') in the books argument
        """
        base_displayed_titles = []
        books_widgets = []

        for index, book in enumerate(books):
            book_widget = BookWidget(
                book,
                self.books_handler,
                self.res_handler,
                self.langs_handler,
                self.qt_signals_handler,
                )
            base_displayed_titles.append(book_widget.book_title_lb.text())
            book_widget.book_title_lb.setText(utils_funcs.set_displayed_names(base_displayed_titles)[index])
            self.books_widgets.append(book_widget)
            books_widgets.append(book_widget)
            
        return books_widgets
    
    def generate_books_pages(self):
        """
        Generate and place the books widget into a pagination view
        """
        
        self.books_widgets = self.create_books_widgets(list(self.shelf._books))
        self.widgets_pages_view_handler.set_widgets(self.books_widgets)

class BookWidget(widgets_pages_view.InPageWidget):
    def __init__(
        self, 
        book: book_sys.Book,
        books_handler: book_sys.BooksHandler,
        res_handler: res_handler.RessourcesHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler, 
        ):
        super().__init__(None, None)
        self.logger = logging.getLogger(__name__)
        self.book = book
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.langs_handler = langs_handler
        self.qt_signals_handler = qt_signals_handler
        self.default_cover_path = self.res_handler.get_res("assets.defaults_covers.book")
        self.main_layout = QtWidgets.QGridLayout(self)
        self.book_cover_lb = QtWidgets.QLabel(self)

        if self.book.cover_path:

            if os.path.exists(self.book.cover_path):
                self.book_cover_lb.setPixmap(QtGui.QPixmap(self.book.cover_path))

            else:
                if self.book.cover_path != self.res_handler.get_res("assets.defaults_covers.default_book_cover"):
                    self.logger.warning(f"Couldn't found cover file for book with ID={self.book.id}, switching to default cover")
                    self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_path))
                    
                else:
                    self.logger.error(f"Couldn't found a valid cover for BookWidget ({self}) !")

        else:
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_path))

        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.fixed_sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.book_title_lb = QtWidgets.QLabel(self.book.title + (f" ({str(self.book.title_suffix)})" if self.book.title_suffix else ""))
        self.book_title_lb.setObjectName("book_title_lb")
        self.book_authors_lb = QtWidgets.QLabel(self.book.authors if self.book.authors else "Unknown")
        self.book_authors_lb.setObjectName("book_authors_lb")
        self.book_summary_te = QtWidgets.QTextEdit()
        self.book_summary_te.setText(self.book.summary if self.book.summary else "")
        self.book_summary_te.setReadOnly(True)
        self.book_summary_te.setObjectName("book_summary_te")
        self.edit_b = QtWidgets.QPushButton(self.langs_handler.get_value("edit_b")) #type: ignore
        self.edit_b.setObjectName("edit_b")
        self.edit_b.setSizePolicy(self.fixed_sp)
        self.delete_b = QtWidgets.QPushButton(self.langs_handler.get_value("delete_b")) #type: ignore
        self.delete_b.setSizePolicy(self.fixed_sp)
        self.delete_b.setObjectName("delete_b")
        self.delete_b.clicked.connect(self.delete_book)
        self.main_layout.addWidget(self.book_title_lb, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.book_authors_lb, 1, 1)
        self.main_layout.addWidget(self.book_summary_te, 2, 1)
        self.main_layout.addWidget(self.edit_b, 3, 1)
        self.main_layout.addWidget(self.delete_b, 4, 1)
        self.main_layout.addWidget(self.book_cover_lb, 1, 0, self.main_layout.rowCount(), 1)
        
    def delete_book(self):
        
        if self.pages_widgets_handler:
            self.logger.info(f"Deleting book with ID={self.book.id}")
            self.qt_signals_handler.edit_progress_msg.emit(self.langs_handler.tr("pages.shelf_details_page.book_deletion_progress_lb", count=1))
            
            try:
                self.books_handler.delete_book(self.book.id)
                
            except my_exceptions.BookNotFoundError:
                self.logger.error(f"Failed to delete book with ID={self.book.id} : Book not found in BooksHandler ({self.books_handler}) !")
                self.qt_signals_handler.notify_sg.emit("error", "", "", "")
                
            self.pages_widgets_handler.delete_widget(self)
            self.qt_signals_handler.edit_progress_msg.emit(" ")
