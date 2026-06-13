
import os
import logging
from PySide6 import QtWidgets, QtCore, QtGui
import widgets_pagination_view
import shiboken6

from app.src import resources_handler as res_handler
from app.utils import my_exceptions
from app.src import langs_handler
from app.src import book_sys
from app.ui import qt_signals_handler
from app.ui import my_widgets_pagination_view
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
        self.PAGE_NAME = "SHELF_DETAILS_PAGE"
        self.shelf = shelf
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.redundant_lang_path = "main_pages.shelf_details_page"
        self.variables_kw = {"shelf":self.shelf}

        #logger
        self.logger = logging.getLogger(__name__)
        
        #Widgets
        self.fix_min_exp_sp = (QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.gen_qss_filepath = self.res_handler.get_res("assets.qss.general")
        self.page_qss_filepath = self.res_handler.get_res("assets.qss.shelf_details_page")
        utils_funcs.load_and_set_ss(self.gen_qss_filepath, self.page_qss_filepath, widget=self, logger=self.logger)
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)
        self.main_widget = QtWidgets.QWidget()
        self.books_widgets = []
        self.research_result_widgets = []
        self.search_le = QtWidgets.QLineEdit()
        self.search_le.setPlaceholderText(self.my_tr(".placeholders.book_research"))
        self.search_le.setSizePolicy(*self.fix_min_exp_sp)
        self.search_le.setMinimumWidth(200)
        self.search_le.setClearButtonEnabled(True)
        self.search_le.returnPressed.connect(lambda: self.search_books(self.search_le.text()))
        self.search_le.textEdited.connect(self.exit_search)

        #widgets pages view handler
        self.widgets_pagination_view_handler = my_widgets_pagination_view.MyWidgetsPaginationView(
            parent=self,
            res_handler=self.res_handler,
            qt_signals_handler=self.qt_signals_handler,
            langs_handler=self.langs_handler,
            max_loadables_pages_count=5,
            widgets_by_page_count=10,
            widgets=[],
        )
        self.widgets_pagination_view_handler.nothing_to_show_page.edit_label_text(self.my_tr(".labels.empty_shelf"))
        self.add_book_b = QtWidgets.QPushButton(self.my_tr("main_pages.shelfs_view_page.buttons.book_creation", False))
        self.add_book_b.clicked.connect(lambda: self.qt_signals_handler.switch_page_sg.emit("BOOK_CREATION_PAGE", True, {}))
        self.widgets_pagination_view_handler.nothing_to_show_page.main_lyt.addWidget(self.add_book_b, 1, 0, QtGui.Qt.AlignmentFlag.AlignCenter)
        #books widgets
        self.generate_books_pages()

        #Adding widgets to layout
        self.main_lyt.addWidget(self.widgets_pagination_view_handler, 1, 0)
        self.main_lyt.addWidget(self.search_le, 0, 0)

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
        self.widgets_pagination_view_handler.widgets = self.books_widgets
        
    @QtCore.Slot(str)
    def search_books(self, given_input: str):
        
        if given_input:
            self.qt_signals_handler.edit_progress_msg.emit(self.my_tr("shared.progress.research", False))
            matches = self.books_handler.get_books(title=(given_input, False, False))
            self.logger.info(f"Found {len(matches)} books which matches with the query")
            
            if matches:
                self.research_result_widgets = self.create_books_widgets(matches)
                self.widgets_pagination_view_handler.widgets = self.research_result_widgets.copy()
                
            else:
                self.widgets_pagination_view_handler.widgets = []
            self.qt_signals_handler.edit_progress_msg.emit(" ")
            
    @QtCore.Slot()
    def exit_search(self):
        
        if not self.search_le.text():
            
            for widget in self.books_widgets:
               if shiboken6.isValid(widget):
                    widget.deleteLater()
                
            self.books_widgets = self.create_books_widgets(list(self.books_handler.books.values()))
            self.widgets_pagination_view_handler.widgets = self.books_widgets
            
            for widget in self.research_result_widgets:
                widget.deleteLater()
                    
            self.research_result_widgets.clear()
            
    def my_tr(self, lang_path: str, fill: bool=True, **kwargs) -> str:
        """Do the same as the 'langs_handler.tr()' attribute, but auto-complete the first part of the 'lang_path' by the value of the 'rebondant_lang_path' attr.\n
        Note that your shortcut lang_path must start by '.' for the auto completion to work.
        
        Parameters
        ----------
        fill (bool=True): specifies wheter or not to fill the begining of the lang_path
        
        Returns
        -------
        str: the translation
        
        Example:
        --------
        you can pass the lang_path '.buttons.do_something' instead of 'main_pages.page_name.buttons.do_something'\n
        if the value of the 'rebondant_lang_path' is 'main_pages.page_name'
        """
        
        if fill and hasattr(self, "redundant_lang_path") and lang_path.startswith("."):
            return self.langs_handler.tr(self.redundant_lang_path+lang_path, **kwargs)
        
        else:
            return self.langs_handler.tr(lang_path, **kwargs)

class BookWidget(widgets_pagination_view.InPageWidget):
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
        self.redundant_lang_path = "main_pages.shelf_details_page"
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
        self.edit_b = QtWidgets.QPushButton(self.my_tr("shared.buttons.edit", False)) #type: ignore
        self.edit_b.setObjectName("edit_b")
        self.edit_b.setSizePolicy(self.fixed_sp)
        self.delete_b = QtWidgets.QPushButton(self.my_tr("shared.buttons.delete", False)) #type: ignore
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
            self.qt_signals_handler.edit_progress_msg.emit(self.my_tr(".progress.book_deletion", count=1))
            
            try:
                self.books_handler.delete_book(self.book.id)
                
            except my_exceptions.BookNotFoundError:
                self.logger.error(f"Failed to delete book with ID={self.book.id} : Book not found in BooksHandler ({self.books_handler}) !")
                self.qt_signals_handler.notify_sg.emit("error", "", "Livre introuvable !", "")
                
            self.pages_widgets_handler.delete_widget(self)
            self.qt_signals_handler.edit_progress_msg.emit(" ")
            
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
