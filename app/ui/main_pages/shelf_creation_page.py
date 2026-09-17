import logging
import os
import shutil
import uuid
from typing import Literal

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import api, book_sys
from app.ui.main_pages import base_page
from app.utils import images_tools, utils_funcs


class EditionModeNotEnabled(Exception):
    def __init__(self, msg: str | None = None):
        """
        Exception usually raised when trying to do something that is only possible if ShelfCreationPage is in edition mode
        """
        self.msg = msg or "Edition mode not enabled !"
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class ShelfCreationPage(base_page.BasePage):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        api: api.API,
        **kwargs,
    ):
        super().__init__(
            parent,
            api,
        )
        self.PAGE_NAME = "SHELF_CREATION_PAGE"
        self.logger = logging.getLogger(__name__)
        self.modes = ("edition", "creation")
        self._current_mode = kwargs.get("mode")
        self.variables_kw = {**kwargs}

        self.PAGE_NAME = "SHELF_CREATION_PAGE"
        if self._current_mode:
            if self._current_mode not in self.modes:
                self.logger.error(
                    f"Mode '{self._current_mode}' is not a valid mode for Shelf Creation Page. Valids mode : {self.modes}"
                )
                raise ValueError(
                    f"Mode '{self._current_mode}' is not a valid mode for Shelf Creation Page. Valids mode : {self.modes}"
                )

        else:
            raise ValueError(
                "No mode provided for Shelf Creation Page initialisation !"
            )
        if self._current_mode == "edition":
            if kwargs.get("shelf"):
                self._shelf: book_sys.Shelf = kwargs["shelf"]

            else:
                self.logger.error(
                    "Shelf Creation Page generated in edit mode, but no shelf object was provided !"
                )
                raise KeyError(
                    "Shelf Creation Page generated in edit mode, but no shelf object was provided !"
                )

        # Shelf cover
        self.default_shelf_cover = self.res_files.get_res(
            "assets.defaults_covers.shelf"
        )
        self.current_shelf_cover = self.default_shelf_cover
        self.shelf_cover_pm = QtGui.QPixmap(self.current_shelf_cover)
        self.shelf_cover_lb = QtWidgets.QLabel()
        self.shelf_cover_lb.setPixmap(self.shelf_cover_pm)
        self.cover_selection_b = QtWidgets.QPushButton(
            self.langs.tr("shared.actions.edit_cover")
        )
        self.cover_selection_b_ico = images_tools.get_svg(
            self.res_files.get_res("assets.icons.edit")
        )
        self.cover_selection_b.setIcon(self.cover_selection_b_ico)
        self.cover_selection_b.clicked.connect(self.set_shelf_cover)
        self.restore_default_cover_b = QtWidgets.QPushButton(
            self.langs.tr("shared.actions.restore_default_cover")
        )
        self.restore_default_cover_b.setIcon(
            images_tools.get_svg(self.res_files.get_res("assets.icons.remove_img"))
        )
        self.restore_default_cover_b.clicked.connect(self.restore_default_cover)

        # Shelf name input widget
        self.title_lb = QtWidgets.QLabel(self.langs.tr("shelf.infos.title"))
        self.title_e = QtWidgets.QLineEdit()
        self.title_e.setMinimumWidth(300)

        # Books selection widgets
        self.books_selection_lb = QtWidgets.QLabel(
            self.langs.tr("shelf.actions.select_books")
        )
        self.draw_children_tree(
            self.books.books_handler.shelves, self.books.books_handler.books
        )
        self.book_research_lb = QtWidgets.QLabel(
            self.langs.tr("shared.actions.search.book")
        )
        self.book_research_e = QtWidgets.QLineEdit()
        self.book_research_e.setMinimumWidth(300)
        self.book_research_e.returnPressed.connect(self.search_book)
        self.stop_research_b = QtWidgets.QPushButton()
        self.existence_msgbox = QtWidgets.QMessageBox()
        self.cancel_b = self.existence_msgbox.addButton(
            self.langs.tr("shared.actions.cancel"),
            QtWidgets.QMessageBox.ButtonRole.RejectRole,
        )
        self.rename_b = self.existence_msgbox.addButton(
            self.langs.tr("shared.actions.rename"),
            QtWidgets.QMessageBox.ButtonRole.AcceptRole,
        )
        self.existence_msgbox.setText(self.langs.tr("shared.msg.add_confirm"))

        # Confirm widgets
        self.confirm_b = QtWidgets.QPushButton(self.langs.tr("shared.actions.done"))
        self.confirm_b.setIcon(
            images_tools.get_svg(self.res_files.get_res("assets.icons.done"))
        )
        self.confirm_b.clicked.connect(self.save_modifications)

        if self._current_mode == "edition":
            self.edition_mode()

        # Add the widgets to the layout
        self.main_lyt.addWidget(
            self.shelf_cover_lb, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_lyt.addWidget(
            self.cover_selection_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_lyt.addWidget(
            self.restore_default_cover_b, 2, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_lyt.addWidget(self.title_lb, 3, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_lyt.addWidget(self.title_e, 4, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.main_lyt.addWidget(
            self.books_selection_lb, 5, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_lyt.addWidget(
            self.book_research_lb, 6, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_lyt.addWidget(
            self.book_research_e, 6, 1, QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.main_lyt.addWidget(self.confirm_b, 8, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

    @property
    def current_mode(self) -> Literal["edition", "creation"]:
        """
        Getter of property 'current_mode'
        """
        return self._current_mode

    @current_mode.setter
    def current_mode(self, new_value: Literal["edition", "creation"]):
        """
        Setter of property 'current_mode'
        """

        if new_value in ("edition", "creation"):
            self._current_mode = new_value

            if self._current_mode == "creation":
                self.edition_mode()

            else:
                self.creation_mode()

        else:
            raise ValueError(f"Wrong argument given to 'current_mode' : {new_value}")

    @property
    def shelf(self):
        """
        Getter of property 'shelf'
        """
        return self._shelf

    @shelf.setter
    def shelf(self, new_value: book_sys.Shelf):
        """
        Setter of property 'shelf'
        """

        if isinstance(new_value, book_sys.Shelf):
            if self._current_mode == "edition":
                self._shelf = new_value
                self.edition_mode()

            else:
                raise EditionModeNotEnabled(
                    "Couldn't set value of 'ShelfCreationPage.shelf while edtion mode isn't enabled !'"
                )

        else:
            raise ValueError(f"Wrong argument given to 'shelf' : {new_value}")

    def creation_mode(self):
        """
        Switch the page to shelf creation mode
        """
        self.qt_signals.emit_signal(
            "switch_page_sg", "SHELF_CREATION_MODE", True, {"mode": "edition"}
        )

    def edition_mode(self):
        if self.shelf:
            # Replace the displayed cover by the shelf's cover
            shelf_cover_path = self.books.get_shelf_cover_path(self.shelf, False)
            if shelf_cover_path:
                self.current_shelf_cover = shelf_cover_path
                self.set_cover_lb_pixmap(self.current_shelf_cover)
            self.title_e.setText(self.shelf.title)

            for title_item in self.objects_title_items:
                if self.shelf.has_book(title_item.data()):
                    title_item.setCheckState(QtCore.Qt.CheckState.Checked)

                if self.shelf.has_shelf(title_item.data()):
                    title_item.setCheckState(QtCore.Qt.CheckState.Checked)

    def set_shelf_cover(self):
        infos = images_tools.select_image()

        if infos and infos[0]:
            img_path = infos[0]
            final_infos = images_tools.prepare_image(
                img_path,
                os.path.join(self.res_files.get_res("tmp"), "shelf_cover.png"),
            )
            self.current_shelf_cover = final_infos[0]
            self.set_cover_lb_pixmap(self.current_shelf_cover)

    def set_cover_lb_pixmap(self, new_path):
        self.shelf_cover_pm.load(new_path)
        self.shelf_cover_lb.setPixmap(self.shelf_cover_pm)

    def restore_default_cover(self):
        """
        Set the cover image to the default value
        """
        if self.current_mode == "edition":
            shelf_cover = self.books.get_shelf_cover_path(self.shelf, False)

            if shelf_cover:
                self.res_files.delete(shelf_cover)
        self.current_shelf_cover = self.default_shelf_cover
        self.set_cover_lb_pixmap(self.current_shelf_cover)

    def draw_children_tree(
        self, shelves_dict: book_sys.ShelvesDict, books_dict: book_sys.BooksDict
    ):

        if hasattr(self, "children_tree"):
            self.main_lyt.removeWidget(self.children_tree)
            self.children_tree.setParent(None)
            self.children_tree.deleteLater()

        if hasattr(self, "children_tree_model"):
            self.children_tree_model.setParent(None)
            self.children_tree_model.deleteLater()

        self.children_tree = QtWidgets.QTreeView()
        self.children_tree.setMinimumHeight(400)
        self.children_tree_model = QtGui.QStandardItemModel()
        self.children_tree_model.setHorizontalHeaderLabels(
            (
                self.langs.tr("shared.infos.type"),
                self.langs.tr("shared.infos.title"),
                self.langs.tr("shared.infos.author"),
                self.langs.tr("shared.infos.edition"),
            )
        )
        self.children_tree.setModel(self.children_tree_model)
        self.objects_title_items = []
        objects = {}
        objects.update(shelves_dict)
        objects.update(books_dict)

        for object in objects.values():
            if self.current_mode == "edition":
                if object == self.shelf:
                    continue

                if object in self.shelf._parent_shelves:
                    continue

            object_type_item = QtGui.QStandardItem("N/A")
            title_item = QtGui.QStandardItem(
                utils_funcs.add_title_suffix(object.title, object.title_suffix)
            )
            title_item.setData(object)
            title_item.setCheckable(True)

            object_author_item = QtGui.QStandardItem("N/A")
            object_edition_item = QtGui.QStandardItem("N/A")

            if isinstance(object, book_sys.Book):
                object_type_item.setText(self.langs.tr("book.infos.object_type"))
                object_type_item.setAccessibleText(
                    self.langs.tr("book.infos.object_type")
                )
                object_author_item.setText(
                    object.authors if object.authors else "Unknown"
                )
                object_edition_item = QtGui.QStandardItem(
                    object.edition if object.edition else "Unknown"
                )

            elif isinstance(object, book_sys.Shelf):
                object_type_item.setText(self.langs.tr("shelf.infos.object_type"))
                object_type_item.setAccessibleText(
                    self.langs.tr("shelf.infos.object_type")
                )
            self.children_tree_model.appendRow(
                (object_type_item, title_item, object_author_item, object_edition_item)
            )
            self.objects_title_items.append(title_item)

        self.children_tree.setColumnWidth(0, 150)
        self.children_tree.setColumnWidth(1, 150)
        self.children_tree.setColumnWidth(2, 150)
        self.children_tree.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.main_lyt.addWidget(self.children_tree, 7, 0, 1, 2)

    def get_matches(self, title) -> list:
        """
        Get shelves which have the same title as this shelf in the books handler.
        In edition mode, this method checks if the title has been modified before searching for matches
        """
        matches = []

        if self.current_mode == "creation":
            matches = self.books.books_handler.get_shelfs(title=(title, True, False))

        elif self.current_mode == "edition" and self.shelf:
            if self.shelf.title != title:
                matches = self.books.books_handler.get_shelfs(
                    title=(title, True, False)
                )

        return matches

    def get_shelf_infos(self) -> dict | None:
        id = uuid.uuid4()

        if self.current_mode == "edition":
            id = self.shelf.id

        shelf_title = self.title_e.text().strip()
        title_suffix = None

        if (
            not shelf_title.lower()
            or shelf_title.lower()
            == self.books.books_handler.default_shelf.title.lower()
        ):  # type: ignore
            self.qt_signals.emit_signal(
                "notify_sg", "error", "", self.langs.tr("shelf.msg.invalid_title"), ""
            )
            return

        matches = self.get_matches(shelf_title)

        if matches:
            title_suffix = utils_funcs.get_title_suffix(matches)

            self.existence_msgbox.setInformativeText(
                f"{self.langs.tr('shelf.msg.shelf_already_exists')} ({title_suffix})\n{self.langs.tr('shared.msg.renaming_future')} '{shelf_title} ({title_suffix})'"
            )
            self.existence_msgbox.exec()

            if not self.existence_msgbox.clickedButton() == self.rename_b:
                return

        books: book_sys.BooksList = []
        child_shelves: book_sys.ShelvesList = []

        for object_title_item in self.objects_title_items:
            if object_title_item.checkState() == QtCore.Qt.CheckState.Checked:
                if isinstance(object_title_item.data(), book_sys.Book):
                    books.append(object_title_item.data())

                elif isinstance(object_title_item.data(), book_sys.Shelf):
                    child_shelves.append(object_title_item.data())

        parents_shelves = []
        if self.current_mode == "edition":
            parents_shelves = self.shelf._parent_shelves

        return {
            "title": shelf_title,
            "title_suffix": title_suffix,
            "books": books,
            "parents_shelves": parents_shelves,
            "children_shelves": child_shelves,
            "id": id,
        }

    def is_original_cover(self):
        """
        Check if the current shelf cover is it's original cover (the one it had before any changes were made)
        """
        original_cover = self.default_shelf_cover

        if self.current_mode == "edition":
            original_cover = self.books.get_book_cover_path(self.shelf)  # type: ignore

        return original_cover == self.current_shelf_cover

    def attach_cover(self, id: str):
        """
        Attach the current cover to the Shelf with `id`
        """

        try:
            self.books.set_cover_for_shelf(id)

        except FileNotFoundError:
            self.logger.error(
                f"Unable to attach cover to Shelf (ID={id}) : Cover file not found"
            )
            self.qt_signals.emit_signal(
                "notify_sg", "error", "Cover Not Found", "Cover file not found !", ""
            )

        except PermissionError:
            self.logger.error(
                f"Unable to attach cover to Shelf (ID={id}) : Permission denied"
            )
            self.qt_signals.emit_signal(
                "notify_sg",
                "error",
                "Permisssion Denied",
                "Access to cover file denied",
                "",
            )
        return True

    def search_book(self):
        query = self.book_research_e.text()

        if query:
            shelves_matches = self.books.books_handler.get_shelfs(title=(query, False))
            books_matches = self.books.books_handler.get_books(title=(query, False))

            shelves_matches_obj_with_id = {}
            books_matches_obj_with_id = {}
            for shelf in shelves_matches:
                shelves_matches_obj_with_id[shelf.id] = shelf

            for book in books_matches:
                books_matches_obj_with_id[book.id] = book

            self.draw_children_tree(
                shelves_matches_obj_with_id, books_matches_obj_with_id
            )

        else:
            self.draw_children_tree(
                self.books.books_handler.shelves, self.books.books_handler.books
            )

    def save_modifications(self):
        shelf_infos = self.get_shelf_infos()

        if shelf_infos:
            if self.current_mode == "creation":
                self.books.books_handler.new_shelf(**shelf_infos)
                if not self.is_original_cover():
                    self.attach_cover(shelf_infos["id"])
                self.qt_signals.emit_signal("shelf_added_sg", shelf_infos["id"])
                QtWidgets.QMessageBox.information(
                    self, "Success", self.langs.tr("shelf.msg.creation_success")
                )
                self.qt_signals.emit_signal("refresh_current_page_sg")

            elif self.current_mode == "edition":
                if self.shelf:
                    self.books.edit_shelf(self.shelf, **shelf_infos)
                    if not self.is_original_cover():
                        self.attach_cover(shelf_infos["id"])
                    self.qt_signals.emit_signal("shelf_edited_sg", self.shelf.id)
                    QtWidgets.QMessageBox.information(
                        self,
                        "Success",
                        self.langs.tr("shelf.msg.edition_success"),
                    )
                    self.qt_signals.emit_signal("close_page_sg")
