import datetime as dt
import logging
import os
import shutil
from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_sys
from app.ui import qt_signals_handler
from app.utils import images_tools


class ShelfCreationPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        books_handler: book_sys.BooksHandler,
        res_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        settings_handler,
        langs_handler,
        **kwargs,
    ):
        super().__init__(parent)
        self.PAGE_NAME = "SHELF_CREATION_PAGE"
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.res_handler = res_handler
        self.qt_signals_handler = qt_signals_handler
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.redundant_lang_path = "main_pages.shelf_creation_page"
        self.modes = ("edition", "creation")
        self.current_mode = kwargs.get("mode")
        self.variables_kw = {**kwargs}

        if self.current_mode:
            if self.current_mode not in self.modes:
                self.logger.error(
                    f"Mode '{self.current_mode}' is not a valid mode for Shelf Creation Page. Valids mode : {self.modes}"
                )
                raise ValueError(
                    f"Mode '{self.current_mode}' is not a valid mode for Shelf Creation Page. Valids mode : {self.modes}"
                )

        else:
            raise ValueError(
                "No mode provided for Shelf Creation Page initialisation !"
            )

        self.main_lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_lyt)
        self.main_widget = QtWidgets.QWidget()
        self.main_widget_lyt = QtWidgets.QGridLayout()
        self.main_widget.setLayout(self.main_widget_lyt)

        # Scroll area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.main_widget)
        self.main_lyt.addWidget(self.scroll_area, 1)

        # Shelf cover
        self.default_shelf_cover = self.res_handler.get_res("assets.defaults_covers.shelf")
        self.current_shelf_cover = self.default_shelf_cover
        self.shelf_cover_pm = QtGui.QPixmap(self.current_shelf_cover)
        self.shelf_cover_lb = QtWidgets.QLabel()
        self.shelf_cover_lb.setPixmap(self.shelf_cover_pm)
        self.cover_selection_b = QtWidgets.QPushButton(self.my_tr("shared.buttons.edit_cover", False))
        self.cover_selection_b_ico = QtGui.QIcon(
            self.res_handler.get_res("assets.icons.edit")
        )
        self.cover_selection_b.setIcon(self.cover_selection_b_ico)
        self.cover_selection_b.clicked.connect(self.set_shelf_cover)

        # Shelf name input widget
        self.name_lb = QtWidgets.QLabel(self.my_tr(".labels.name"))
        self.name_e = QtWidgets.QLineEdit()
        self.name_e.setMinimumWidth(300)

        # Books selection widgets
        self.books_selection_lb = QtWidgets.QLabel(self.my_tr(".labels.books_selection"))
        self.book_research_lb = QtWidgets.QLabel(self.my_tr("shared.labels.research", False))
        self.book_research_e = QtWidgets.QLineEdit()
        self.book_research_e.setMinimumWidth(300)
        self.book_research_e.returnPressed.connect(self.search_book)
        self.stop_research_b = QtWidgets.QPushButton()
        self.existence_msgbox = QtWidgets.QMessageBox()
        self.cancel_b = self.existence_msgbox.addButton(self.my_tr("shared.buttons.cancel", False), QtWidgets.QMessageBox.ButtonRole.RejectRole)
        self.rename_b = self.existence_msgbox.addButton(self.my_tr("shared.buttons.rename", False), QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        self.existence_msgbox.setText(self.my_tr("shared.notifications.add_confirm", False))

        self.draw_books_tree(self.books_handler.books)

        # Confirm widgets
        self.confirm_b = QtWidgets.QPushButton(self.my_tr("shared.buttons.done", False))
        self.confirm_b.setIcon(
            QtGui.QIcon(self.res_handler.get_res("assets.icons.done"))
        )
        self.confirm_b.clicked.connect(self.create_shelf)

        # Add the widgets to the layout
        self.main_widget_lyt.addWidget(
            self.shelf_cover_lb, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.cover_selection_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.name_lb, 2, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.name_e, 3, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.books_selection_lb, 4, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.book_research_lb, 5, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.book_research_e, 5, 1, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_widget_lyt.addWidget(
            self.confirm_b, 7, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )

        if self.current_mode == "edition":
            if kwargs.get("shelf"):
                self.shelf: book_sys.Shelf|None = kwargs.get("shelf") 
                self.edition_mode()

            else:
                self.logger.error(
                    "Shelf Creation Page generated in edit mode, but no shelf object was provided !"
                )
                raise KeyError(
                    "Shelf Creation Page generated in edit mode, but no shelf object was provided !"
                )

    def edition_mode(self):
        if self.shelf:
            self.name_e.setText(self.shelf.name)

            for title_item in self.books_title_items:
                if self.shelf.has_book(title_item.data()):
                    title_item.setCheckState(QtCore.Qt.CheckState.Checked)

    def set_shelf_cover(self):
        infos = images_tools.select_image()
        self.logger.debug(f"Shelf cover infos={infos}")

        if infos and infos[0]:
            img_path = infos[0]
            final_infos = images_tools.prepare_image(
                img_path, os.path.join(self.res_handler.get_res("tmp"), "shelf_cover.png")
            )
            self.current_shelf_cover = final_infos[0]
            self.set_cover_lb_pixmap(self.current_shelf_cover)

    def set_cover_lb_pixmap(self, new_path):
        self.shelf_cover_pm.load(new_path)
        self.shelf_cover_lb.setPixmap(self.shelf_cover_pm)

    def draw_books_tree(self, books_dict: book_sys.BooksDict):

        if hasattr(self, "books_tree"):
            self.main_widget_lyt.removeWidget(self.books_tree)
            self.books_tree.setParent(None)
            self.books_tree.deleteLater()

        if hasattr(self, "books_tree_model"):
            self.books_tree_model.setParent(None)
            self.books_tree_model.deleteLater()

        self.books_tree = QtWidgets.QTreeView()
        self.books_tree.setMinimumHeight(400)
        self.books_tree_model = QtGui.QStandardItemModel()
        self.books_tree_model.setHorizontalHeaderLabels((self.my_tr("shared.labels.title", False), self.my_tr("shared.labels.author", False), self.my_tr("shared.labels.edition", False)))
        self.books_tree.setModel(self.books_tree_model)
        self.books_title_items = []

        # Books items

        for book in books_dict.values():
            book_title_item = QtGui.QStandardItem(
                book.title + (f" ({book.title_suffix})" if book.title_suffix else "")
            )
            book_title_item.setData(book)
            book_title_item.setCheckable(True)
            book_author_item = QtGui.QStandardItem(
                book.authors if book.authors else "Unknown"
            )
            book_edition_item = QtGui.QStandardItem(
                book.edition if book.edition else "Unknown"
            )
            self.books_tree_model.appendRow(
                (book_title_item, book_author_item, book_edition_item)
            )
            self.books_title_items.append(book_title_item)

        self.books_tree.setColumnWidth(0, 150)
        self.books_tree.setColumnWidth(1, 150)
        self.books_tree.setColumnWidth(2, 150)
        self.books_tree.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.main_widget_lyt.addWidget(self.books_tree, 6, 0, 1, 2)
        
    def check_name_existence(self, name):
        return self.books_handler.get_shelfs(name=(name, True, False))

    def get_shelf_infos(self) -> dict | None:
        id = str(dt.datetime.timestamp(dt.datetime.now()))

        shelf_name = self.name_e.text()
        name_suffix = None
        
        if not shelf_name.lower() or shelf_name.lower() == self.books_handler.default_shelf.name.lower(): # type: ignore
            self.qt_signals_handler.notify_sg.emit("error", "", "Nom d'étagère invalide", "")
            return
        
        if self.current_mode == "creation":
        
            try:
                names_matches = self.check_name_existence(shelf_name)
                
            except AttributeError:
                self.logger.exception(f"Unable to check {shelf_name=} existence for on creating shelf !")
                return
            
            else:
                if names_matches:
                    self.existence_msgbox.setInformativeText(f"{self.my_tr(".notifications.shelf_already_exists")} ({len(names_matches)})\n{self.my_tr("shared.notifications.renaming_future", False)} '{shelf_name} ({len(names_matches)})'")
                    self.existence_msgbox.exec()
                    
                    if self.existence_msgbox.clickedButton() == self.rename_b:
                        name_suffix = len(names_matches)
                    
                    else:
                        return
                        
                              
        books: book_sys.BooksList = []

        for book_title_item in self.books_title_items:
            if book_title_item.checkState() == QtCore.Qt.CheckState.Checked:
                books.append(book_title_item.data())
                
                final_img_path = self.current_shelf_cover 

        if self.current_shelf_cover != self.default_shelf_cover:
            final_img_path = os.path.join(
                self.res_handler.get_res("data.bookshelves.covers"), f"{id.replace('.', '_')}.png"
            )
            done = self.move_cover_img(final_img_path)
            
            if not done:
                return
            
            self.current_shelf_cover = final_img_path
            self.set_cover_lb_pixmap(final_img_path)

        return {
            "name": shelf_name,
            "name_suffix": name_suffix,
            "books": books,
            "id": id,
            "cover_path": self.current_shelf_cover
            if self.current_shelf_cover != self.default_shelf_cover
            else None,
        }

    def move_cover_img(self, dest_path):

        try:
            shutil.copy2(self.current_shelf_cover, dest_path)

        except Exception:
            self.logger.exception(
                f"Unable to move cover file from tmp path to '{dest_path}' due to error : "
            )
            self.qt_signals_handler.notify_sg.emit("error", "", "", "")
            
        else:
            return True

    def search_book(self):
        query = self.book_research_e.text()

        if query:
            query_results = self.books_handler.get_books(title=(query, False))
            matches = {}

            for result in query_results:
                matches[result.id] = result

            self.draw_books_tree(matches)

        else:
            self.draw_books_tree(self.books_handler.books)

    def create_shelf(self):
        shelf_infos = self.get_shelf_infos()

        if shelf_infos:
            if self.current_mode == "creation":
                self.books_handler.new_shelf(**shelf_infos)
                #QtWidgets.QMessageBox.information(self, "Terminé", "Etagère crée")

            elif self.current_mode == "edition":
                if self.shelf:
                    edited_shelf = self.books_handler.create_shelf(**shelf_infos)
                    self.books_handler.edit_shelf(self.shelf.id, edited_shelf)
                    #QtWidgets.QMessageBox.information(
                    #    self, "Terminé", "Etagère modifiée"
                    #)
                    
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
            return self.langs_handler.tr(self.redundant_lang_path+lang_path)
        
        else:
            return self.langs_handler.tr(lang_path)

            
