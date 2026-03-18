import datetime as dt
import logging
import os
import shutil
import traceback
from pathlib import Path
from typing import Literal

from PySide6 import QtCore, QtGui, QtWidgets

from app.src import book_stuff
from app.ui import qt_signals_handler
from app.utils import images_tools, paths


class BookCreationPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        books_handler: book_stuff.BooksHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(parent)
        self.books_handler = books_handler
        self.qt_signals_handler = qt_signals_handler
        self.logger = logging.getLogger(__name__)
        self.icons_folder = paths.ICONS_PATH
        self.today_date_dt = dt.date.today()

        self.basic_book_infos = {
            "title": "Titre : ",
            "authors": "Auteur : ",
            "edition": "Edition : ",
            "summary": "Résumé : ",
            "tot_pages": "Pages totales : ",
        }
        self.basic_book_info_ew = {}
        self.left_alignment = QtCore.Qt.AlignmentFlag.AlignLeft
        self.top_alignment = QtCore.Qt.AlignmentFlag.AlignTop

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.container_widget = QtWidgets.QWidget(self)
        self.container_widget_layout = QtWidgets.QGridLayout(self.container_widget)
        self.container_widget_layout.setAlignment(self.left_alignment)
        self.container_widget_layout.setSpacing(30)
        self.container_widget.setLayout(self.container_widget_layout)
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container_widget)

        # Exit Widget
        self.exit_b = QtWidgets.QPushButton("Fermer")
        self.exit_b.setIcon(
            QtGui.QIcon(os.path.join(self.icons_folder, "cross_ico.png"))
        )
        self.exit_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.exit_b.clicked.connect(
            lambda: self.qt_signals_handler.go_previous_page_sg.emit(True)
        )

        # Cover widgets
        self.default_cover_img = os.path.join(
            paths.DEFAULT_COVERS_PATH, "default_book_cover.png"
        )
        self.cover_image = self.default_cover_img
        self.book_cover_lb = QtWidgets.QLabel()
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_img))
        self.edit_cover_b = QtWidgets.QPushButton("Changer la couverture")
        self.edit_cover_b.setIcon(
            QtGui.QIcon(os.path.join(paths.ICONS_PATH, "edit_ico.png"))
        )
        self.edit_cover_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.edit_cover_b.clicked.connect(self.set_book_cover)

        # Book infos widgets
        row = 3
        for (
            key,
            value,
        ) in self.basic_book_infos.items():
            lb = QtWidgets.QLabel(value)
            ew = QtWidgets.QLineEdit() if key != "summary" else QtWidgets.QTextEdit()

            if key == "summary":
                lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            elif key == "tot_pages":
                ew.textEdited.connect(lambda: self.check_int(ew.text(), ew))  # type: ignore

            ew.setMaximumWidth(300)
            self.container_widget_layout.addWidget(lb, row, 0)
            self.container_widget_layout.addWidget(ew, row, 1)
            self.basic_book_info_ew[key] = ew
            row += 1

        # Book status widgets
        self.book_status_lb = QtWidgets.QLabel("status : ")
        self.book_status_combob = QtWidgets.QComboBox()
        self.book_status_combob.addItem("Non lut", "unread")
        self.book_status_combob.addItem("En cours", "on_reading")
        self.book_status_combob.addItem("Terminé", "finished")
        self.book_status_combob.currentIndexChanged.connect(
            lambda: self.set_book_status(self.book_status_combob.currentData())
        )
        self.book_status_widget = QtWidgets.QWidget(self)
        self.book_status_widget_layout = QtWidgets.QGridLayout()
        self.book_status_widget.setLayout(self.book_status_widget_layout)
        self.alr_read_pages_lb = QtWidgets.QLabel("Pages lues : ")
        self.alr_read_pages_le = QtWidgets.QLineEdit()
        self.alr_read_pages_le.textEdited.connect(
            lambda: self.check_int(
                self.alr_read_pages_le.text(), self.alr_read_pages_le
            )
        )
        self.alr_read_pages_le.setMaximumWidth(300)
        self.today_date = QtCore.QDate(
            self.today_date_dt.year, self.today_date_dt.month, self.today_date_dt.day
        )
        self.starting_read_date_lb = QtWidgets.QLabel("Commencé le : ")
        self.starting_read_date_de = QtWidgets.QDateEdit()
        self.starting_read_date_de.setDate(self.today_date)
        self.starting_read_date_de.setCalendarPopup(True)
        self.starting_read_date_de.setMaximumWidth(300)
        self.end_read_date_lb = QtWidgets.QLabel("Terminé le : ")
        self.end_read_date_de = QtWidgets.QDateEdit()
        self.end_read_date_de.setDate(self.today_date)
        self.end_read_date_de.setCalendarPopup(True)
        self.end_read_date_de.setMaximumWidth(300)
        self.set_book_status("unread")
        self.book_status_widget_layout.addWidget(self.alr_read_pages_lb, 0, 0)
        self.book_status_widget_layout.addWidget(self.alr_read_pages_le, 0, 1)
        self.book_status_widget_layout.addWidget(self.starting_read_date_lb, 1, 0)
        self.book_status_widget_layout.addWidget(self.starting_read_date_de, 1, 1)
        self.book_status_widget_layout.addWidget(self.end_read_date_lb, 2, 0)
        self.book_status_widget_layout.addWidget(self.end_read_date_de, 2, 1)

        # Shelfs widgets
        self.shelfs_selection_lb = QtWidgets.QLabel("Etageres : ")
        self.shelfs_selection_cbs = {}
        self.shelfs_selection_widget = QtWidgets.QWidget(self)
        self.shelfs_selection_layout = QtWidgets.QVBoxLayout(
            self.shelfs_selection_widget
        )
        self.shelfs_selection_widget.setLayout(self.shelfs_selection_layout)
        self.shelfs_selection_scroll_area = QtWidgets.QScrollArea(self)
        self.shelfs_selection_scroll_area.setMaximumWidth(300)
        self.shelfs_selection_scroll_area.setMinimumHeight(400)
        self.shelfs_selection_scroll_area.setWidgetResizable(True)
        self.shelfs_selection_scroll_area.setWidget(self.shelfs_selection_widget)

        shelfs_names = []
        for shelf in self.books_handler.books_shelfs.values():
            matches_count = 0
            displayed_name = shelf.name
            shelfs_names.append(shelf.name)

            for name in shelfs_names:
                if name == shelf.name and not shelf.name:
                    displayed_name = (
                        f"[Unnamed]-{dt.datetime.fromtimestamp(float(shelf.id)).date()}"
                    )

                    if matches_count:
                        displayed_name += f" ({matches_count})"

                    matches_count += 1

            shelf_cb = QtWidgets.QCheckBox(displayed_name)
            self.shelfs_selection_cbs[shelf.id] = shelf_cb
            self.shelfs_selection_layout.addWidget(shelf_cb)

        self.existence_msgbox = QtWidgets.QMessageBox()
        self.existence_msgbox.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
        )
        self.existence_msgbox.setText("Voulez vous vraiment ajouter ce livre ?")

        self.add_b = QtWidgets.QPushButton("Ajouter")
        self.add_b.clicked.connect(self.create_book)

        # Add the widgets
        self.main_layout.addWidget(self.exit_b, 0)
        self.container_widget_layout.addWidget(self.book_cover_lb, 1, 0)
        self.container_widget_layout.addWidget(self.edit_cover_b, 2, 0)
        self.container_widget_layout.addWidget(
            self.book_status_lb, self.container_widget_layout.rowCount() + 1, 0
        )
        self.container_widget_layout.addWidget(
            self.book_status_combob, self.container_widget_layout.rowCount() + 1, 1
        )
        self.container_widget_layout.addWidget(
            self.book_status_widget,
            self.container_widget_layout.rowCount() + 1,
            0,
            2,
            0,
        )
        self.container_widget_layout.addWidget(
            self.shelfs_selection_lb, self.container_widget_layout.rowCount() + 1, 0
        )
        self.container_widget_layout.addWidget(
            self.shelfs_selection_scroll_area,
            self.container_widget_layout.rowCount() + 1,
            0,
        )
        self.container_widget_layout.addWidget(
            self.add_b, self.container_widget_layout.rowCount() + 1, 0
        )
        self.main_layout.addWidget(self.scroll_area, 1)

    def set_book_status(self, status: Literal["finished", "on_reading", "unread"]):
        """
        Set the book status and draw the appriopriate widgets

        Args:
        - status (str): the book status ("finished", "on_read" or "unread")
        """
        if status == "finished":
            self.alr_read_pages_le.setEnabled(False)
            self.starting_read_date_de.setEnabled(True)
            self.end_read_date_de.setEnabled(True)

        elif status == "on_reading":
            self.alr_read_pages_le.setEnabled(True)
            self.starting_read_date_de.setEnabled(True)
            self.end_read_date_de.setEnabled(False)

        elif status == "unread":
            self.alr_read_pages_le.setEnabled(False)
            self.starting_read_date_de.setEnabled(False)
            self.end_read_date_de.setEnabled(False)

    def check_int(self, text: str, le: QtWidgets.QLineEdit | None = None):
        """
        Check if all characters in <text> are numbers return it, and eventually edit the PySide6.QtWidgets.QLineEdit if it is given

        Args:
        - text (str): the text to check
        - le (PySide6.QtWidgets.QLineEdit): the QLineEdit widget to change
        """

        for c in text:
            if not c.isdigit():
                text = text.replace(c, "")

        if le:
            le.setText(text)

        return text

    def set_default_cover(self):
        self.cover_image = self.default_cover_img
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.default_cover_img))

    def set_book_cover(self):
        infos = images_tools.select_image()

        if infos:
            if infos[0]:
                final_infos = images_tools.prepare_image(
                    infos[0], os.path.join(paths.TMP_DIR_PATH, "book_cover.png")
                )
                self.cover_image = final_infos[0]
                self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def set_cover_lb_pixmap(self, new_path):
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def check_existence(self, **kwargs):
        """
        Check if a book who match with the requirements specified iin kwargs exists in the current books handler, and return the standard output of the method <get_book> of the books handler
        """
        return self.books_handler.get_book(**kwargs)

    def get_book_infos(self):
        books_infos = {}

        for key, w in self.basic_book_info_ew.items():
            if isinstance(w, QtWidgets.QLineEdit):
                text = w.text()

                if key == "tot_pages":
                    books_infos[key] = text if text else 0

                else:
                    if text:
                        books_infos[key] = text

            elif isinstance(w, QtWidgets.QTextEdit):
                text = w.toPlainText()

                if text:
                    books_infos[key] = text

        try:
            matches = self.check_existence(
                title=(books_infos.get("title"), True, False),
                authors=(books_infos.get("authors"), True, False),
            )

        except AttributeError:
            self.logger.error(f"{traceback.format_exc()}")
            return {}

        if matches:
            self.logger.debug(
                f"Found {len(matches)} {[x.internal_id for x in matches]} books which have the same authors and the same title that the on creating book !"
            )
            self.existence_msgbox.setInformativeText(
                f"{len(matches)} livres ayant le même titre et/ou le même autheur que celui-ci ont été trouvés"
            )
            answer = self.existence_msgbox.exec()

            if answer == QtWidgets.QMessageBox.StandardButton.No:
                return

        books_infos["internal_id"] = str(dt.datetime.timestamp(dt.datetime.now()))

        if str(self.cover_image) != self.default_cover_img:
            final_cover_image = os.path.join(
                paths.BOOKS_COVERS_PATH,
                f"{books_infos['internal_id'].replace('.', '_')}.png",
            )

            if cover_img_path.exists():
                shutil.copy2(
                    self.cover_image,
                    os.path.join(
                        paths.BOOKS_COVERS_PATH,
                        final_cover_image,
                    ),
                )
                self.cover_image = final_cover_image
                self.set_cover_lb_pixmap(self.cover_image)

        books_infos["cover_img_path"] = str(self.cover_image)

        books_infos["status"] = self.book_status_combob.currentData()

        if self.alr_read_pages_le.isEnabled():
            text = self.alr_read_pages_le.text()
            books_infos["alr_read_pages"] = int(text) if text else 0

        if self.starting_read_date_de.isEnabled():
            books_infos["starting_read_date"] = (
                self.starting_read_date_de.date().toString(QtCore.Qt.DateFormat.ISODate)
            )

        if self.end_read_date_de.isEnabled():
            books_infos["end_read_date"] = self.end_read_date_de.date().toString(
                QtCore.Qt.DateFormat.ISODate
            )

        books_infos["shelfs_ids"] = []

        for shelf_id, shelf_selection_cbs in self.shelfs_selection_cbs.items():
            if shelf_selection_cbs.isChecked():
                books_infos["shelfs_ids"].append(shelf_id)

        return books_infos

    def create_book(self):
        books_infos = self.get_book_infos()

        if books_infos:
            try:
                self.books_handler.new_book(**books_infos)

            except Exception:
                self.logger.error(traceback.format_exc())

            else:
                QtWidgets.QMessageBox.information(self, "Terminé", "Livre ajouté !")
