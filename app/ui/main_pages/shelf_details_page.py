import logging
import os

import shiboken6
import widgets_pagination_view
from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys, langs_handler
from app.src import resources_handler as res_handler
from app.ui import my_widgets_pagination_view, qt_signals_handler
from app.ui.main_pages import base_page
from app.ui.main_pages.shelfs_view_page import DefaultShelfWidget, ShelfWidget
from app.utils import images_tools, my_exceptions, utils_funcs


class UnknownChildrenError(Exception):
    def __init__(self, children):
        """
        Exception usually raised when the type of one of the `Shelf` children is not supported
        """
        super().__init__()
        self.msg = f"Unknown shelf children type : {type(children)}"

    def __str__(self):
        return self.msg


class ShelfDetailsPage(base_page.BasePage):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        shelf: book_sys.Shelf,
        books_handler: book_sys.BooksHandler,
        res_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler,
        langs_handler,
    ):

        super().__init__(
            parent, res_handler, settings_handler, langs_handler, qt_signals_handler
        )
        self.PAGE_NAME = "SHELF_DETAILS_PAGE"
        self.shelf = shelf
        self.books_handler = books_handler
        self.variables_kw = {"shelf": self.shelf}

        # logger
        self.logger = logging.getLogger(__name__)

        # Widgets
        self.fix_min_exp_sp = (
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.shelf_details_page"),
            widget=self,
            logger=self.logger,
        )
        if self.shelf != self.books_handler.default_shelf:
            self.shelf_basic_infos_w = BasicShelfInfosWidget(
                self.shelf,
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.langs_handler,
            )

        else:
            self.shelf_basic_infos_w = DefaultShelfWidget(
                self.shelf,
                self.books_handler,
                self.res_handler,
                self.qt_signals_handler,
                self.langs_handler,
            )
        self.shelf_basic_infos_w.sub_widget.view_b.setVisible(False)
        self.shelf_content_widgets = []
        self.research_result_widgets = []
        self.search_le = QtWidgets.QLineEdit()
        self.search_le.setProperty("role", "SearchField")
        self.search_le.setObjectName("SearchInShelfField")
        self.search_le.setPlaceholderText(
            self.langs_handler.tr("shared.actions.search.base")
        )
        self.search_le.setSizePolicy(*self.fix_min_exp_sp)
        self.search_le.setMinimumWidth(200)
        self.search_le.setClearButtonEnabled(True)
        self.search_le.returnPressed.connect(
            lambda: self.search_books(self.search_le.text())
        )
        self.search_le.textEdited.connect(self.exit_search)

        # widgets pages view handler
        self.widgets_pagination_view_handler = (
            my_widgets_pagination_view.MyWidgetsPaginationView(
                parent=self,
                res_handler=self.res_handler,
                qt_signals_handler=self.qt_signals_handler,
                langs_handler=self.langs_handler,
                max_loadables_pages_count=5,
                widgets_by_page_count=10,
                widgets=[],
            )
        )
        self.sep = QtWidgets.QFrame()
        self.sep.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.widgets_pagination_view_handler.setObjectName("ShelfContentViewer")
        self.widgets_pagination_view_handler.nothing_to_show_page.edit_label_text(
            self.langs_handler.tr("shared.msg.nothing_to_show")
        )
        self.add_book_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.book_creation")
        )
        self.add_book_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "BOOK_CREATION_PAGE", True, {}
            )
        )
        self.add_shelf_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.shelf_creation")
        )
        self.add_shelf_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "SHELF_CREATION_PAGE", True, {"mode": "creation"}
            )
        )
        self.widgets_pagination_view_handler.nothing_to_show_page.main_lyt.addWidget(
            self.add_book_b, 1, 0, QtGui.Qt.AlignmentFlag.AlignCenter
        )
        self.widgets_pagination_view_handler.nothing_to_show_page.main_lyt.addWidget(
            self.add_shelf_b, 2, 0, QtGui.Qt.AlignmentFlag.AlignCenter
        )
        # books widgets
        self.generate_widgets_pages()

        # Adding widgets to layout
        self.main_lyt.addWidget(
            self.search_le, 0, 2, QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.main_lyt.addWidget(
            self.shelf_basic_infos_w, 1, 0, QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.main_lyt.addWidget(self.sep, 1, 1)
        self.main_lyt.addWidget(self.widgets_pagination_view_handler, 1, 2)

    def create_children_widgets(
        self, books: book_sys.BooksList, shelves: book_sys.ShelvesList
    ):
        """
        Generate widget ('BookWidget') for every book ('book_sys.Book') in the books argument
        """
        children_widgets = []
        children_obj = []
        children_obj.extend(shelves)
        children_obj.extend(books)
        for object in children_obj:
            widget = None
            if isinstance(object, book_sys.Book):
                widget = BookWidget(
                    object,
                    self.books_handler,
                    self.res_handler,
                    self.langs_handler,
                    self.qt_signals_handler,
                )

            if isinstance(object, book_sys.Shelf):
                widget = ShelfWidget(
                    object,
                    self.books_handler,
                    self.res_handler,
                    self.qt_signals_handler,
                    self.langs_handler,
                )
            children_widgets.append(widget)

        return children_widgets

    def generate_widgets_pages(self):
        """
        Generate and place the books widget into a pagination view
        """

        self.children_widget = self.create_children_widgets(
            self.shelf._books, self.shelf._children_shelves
        )
        self.widgets_pagination_view_handler.widgets = self.children_widget

    @QtCore.Slot(str)
    def search_books(self, given_input: str):

        if given_input:
            # Editing the message displayed on the nothing_to_show page
            self.widgets_pagination_view_handler.nothing_to_show_page.edit_label_text(
                self.langs_handler.tr("shared.msg.no_search_result")
            )

            self.qt_signals_handler.edit_progress_msg.emit(
                self.langs_handler.tr("shared.msg.search_in_progress")
            )
            books_matches = self.books_handler.get_obj(
                self.shelf._books, title=(given_input, False, False)
            )
            shelves_matches = self.books_handler.get_obj(
                self.shelf._children_shelves, title=(given_input, False, False)
            )
            self.logger.info(
                f"Found {len(books_matches)} books and {len(shelves_matches)} shelves which matches with the query"
            )

            if books_matches or shelves_matches:
                self.research_result_widgets = self.create_children_widgets(
                    books_matches, shelves_matches
                )
                self.widgets_pagination_view_handler.widgets = (
                    self.research_result_widgets.copy()
                )

            else:
                self.widgets_pagination_view_handler.widgets = []
            self.qt_signals_handler.edit_progress_msg.emit(" ")

    @QtCore.Slot()
    def exit_search(self):

        if not self.search_le.text():
            for widget in self.shelf_content_widgets:
                if shiboken6.isValid(widget):
                    widget.deleteLater()

            self.shelf_content_widgets = self.create_children_widgets(
                list(self.shelf._books),
                list(self.shelf._children_shelves),
            )
            self.widgets_pagination_view_handler.widgets = self.shelf_content_widgets

            for widget in self.research_result_widgets:
                widget.deleteLater()

            self.research_result_widgets.clear()
            self.widgets_pagination_view_handler.nothing_to_show_page.edit_label_text(
                self.langs_handler.tr("shelf.msg.empty_shelf")
            )


class BasicShelfInfosWidget(ShelfWidget):
    def __init__(
        self, shelf, books_handler, res_handler, qt_signals_handler, langs_handler
    ):
        super().__init__(
            shelf, books_handler, res_handler, qt_signals_handler, langs_handler
        )
        self.sub_widget.delete_b.clicked.disconnect(self.delete_shelf)
        self.sub_widget.delete_b.clicked.connect(self.delete_shelf)
        self.sub_widget.view_b.hide()

    @QtCore.Slot()
    def delete_shelf(self):
        """
        An override of the `delete_shelf` method, which do basically the same, without deleting this widget from the widgets pagination handler, since there is *no* pagination handler
        """
        self.qt_signals_handler.edit_progress_msg.emit(
            self.langs_handler.tr("shelf.msg.shelf_deletion", count=1)
        )
        self.logger.error(f"Deleting 1 Shelf (ID={self.shelf.id})...")
        try:
            print(self.shelf.str_id())
            self.books_handler.delete_shelf(self.shelf.str_id())

        except my_exceptions.BooksShelfNotFoundError:
            self.logger.error(
                f"Unable to delete Shelf (ID={self.shelf.id}) : Shelf not found !"
            )
            self.qt_signals_handler.notify_sg.emit(
                "error", "", self.langs_handler.tr("shelf.msg.shelf_not_found"), ""
            )
            self.qt_signals_handler.edit_progress_msg.emit(" ")

        except Exception:
            self.logger.exception(
                f"Unable to delete Shelf (ID={self.shelf.id}) : due to the following exception : "
            )
            self.qt_signals_handler.notify_sg.emit("error", "", "", "")
            self.qt_signals_handler.edit_progress_msg.emit(" ")

        else:
            self.qt_signals_handler.edit_progress_msg.emit(" ")
            self.qt_signals_handler.close_page_sg.emit()


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

        self.main_layout = QtWidgets.QGridLayout(self)
        self.book_title_lb = QtWidgets.QLabel(
            utils_funcs.add_title_suffix(book.title, title_suffix=book.title_suffix)
        )
        self.sub_widget = SubBookWidget(
            self.book,
            self.books_handler,
            self.res_handler,
            self.langs_handler,
            self.qt_signals_handler,
        )
        self.book_title_lb.setObjectName("BookTitleLabel")
        self.sub_widget.delete_b.clicked.connect(self.delete_book)
        self.max_sp = QtWidgets.QSizePolicy()
        self.max_sp.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Maximum)
        self.max_sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Maximum)
        self.setSizePolicy(QtWidgets.QSizePolicy())
        self.main_layout.addWidget(
            self.book_title_lb,
            0,
            0,
            QtCore.Qt.AlignmentFlag.AlignLeft,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self.main_layout.addWidget(
            self.sub_widget,
            1,
            0,
            QtCore.Qt.AlignmentFlag.AlignLeft,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )

    def delete_book(self):

        if self.pages_widgets_handler:
            self.logger.info(f"Deleting book with ID={self.book.id}")
            self.qt_signals_handler.edit_progress_msg.emit(
                self.langs_handler.tr("book.msg.book_deletion", count=1)
            )

            try:
                self.books_handler.delete_book(self.book.str_id())

            except my_exceptions.BookNotFoundError:
                self.logger.error(
                    f"Failed to delete book with ID={self.book.id} : Book not found in BooksHandler ({self.books_handler}) !"
                )
                self.qt_signals_handler.notify_sg.emit(
                    "error",
                    "",
                    self.langs_handler.tr("book.msg.book_not_found"),
                    "",
                )

            self.pages_widgets_handler.delete_widget(self)
            self.qt_signals_handler.edit_progress_msg.emit(" ")


class SubBookWidget(QtWidgets.QWidget):
    def __init__(
        self,
        book: book_sys.Book,
        books_handler: book_sys.BooksHandler,
        res_handler: res_handler.RessourcesHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(None)
        self.logger = logging.getLogger(__name__)
        self.book = book
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.langs_handler = langs_handler
        self.qt_signals_handler = qt_signals_handler
        self.default_cover_path = self.res_handler.get_res(
            "assets.defaults_covers.book"
        )
        self.main_layout = QtWidgets.QGridLayout(self)
        self.book_cover_lb = QtWidgets.QLabel(self)
        self.cover_path = (
            self.books_handler.get_book_cover_path(self.book, False)
            or self.default_cover_path
        )
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_path))
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.fixed_sp = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.book_authors_lb = QtWidgets.QLabel(
            self.book.authors if self.book.authors else "Unknown"
        )
        self.book_authors_lb.setObjectName("BookAuthorLabel")
        self.book_reading_state_lb = QtWidgets.QLabel()
        self.book_reading_state_lb.setObjectName("BookReadingStateLabel")
        self.display_reading_state()
        self.book_summary_te = QtWidgets.QTextEdit()
        self.book_summary_te.setText(self.book.summary if self.book.summary else "")
        self.book_summary_te.setMinimumSize(350, 120)
        self.book_summary_te.setMaximumSize(400, 120)
        self.book_summary_te.setReadOnly(True)
        self.book_summary_te.setObjectName("BookSummary")
        self.edit_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.edit")
        )  # type: ignore
        self.edit_b.setObjectName("EditButton")
        self.edit_b.setIcon(
            images_tools.get_svg(self.res_handler.get_res("assets.icons.edit"))
        )
        self.edit_b.setSizePolicy(self.fixed_sp)
        self.edit_b.clicked.connect(
            lambda: self.qt_signals_handler.switch_page_sg.emit(
                "BOOK_CREATION_PAGE",
                True,
                {"edition_mode_enabled": True, "book": self.book},
            )
        )
        self.delete_b = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.delete")
        )  # type: ignore
        self.delete_b.setIcon(
            images_tools.get_svg(self.res_handler.get_res("assets.icons.exit"), "red")
        )
        self.delete_b.setSizePolicy(self.fixed_sp)
        self.delete_b.setProperty("role", "DeleteButton")
        self.main_layout.addWidget(self.book_authors_lb, 0, 1)
        self.main_layout.addWidget(self.book_reading_state_lb, 1, 1)
        self.main_layout.addWidget(
            self.book_summary_te,
            2,
            1,
            QtCore.Qt.AlignmentFlag.AlignLeft,
            QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self.main_layout.addWidget(
            self.edit_b,
            3,
            1,
        )
        self.main_layout.addWidget(
            self.delete_b,
            4,
            1,
        )
        self.main_layout.addWidget(
            self.book_cover_lb,
            0,
            0,
            5,
            1,
        )

    def display_reading_state(self):
        """
        Set the text displayed by the book reading state label
        """
        if self.book.status == "unread":
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.unread')} - {self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        elif self.book.status == "on_reading":
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.currently_reading')} - {self.book.alr_read_pages}/{self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        elif self.book.status == "finished":
            self.book_reading_state_lb.setText(
                f"{self.langs_handler.tr('book.infos.reading_state.finished')} - {self.langs_handler.tr('shared.infos.pages_count_args', count=self.book.tot_pages)}"
            )

        else:
            self.logger.warning(
                f"Book ID={self.book.id} has an unknown reading state '{self.book.status}'"
            )
