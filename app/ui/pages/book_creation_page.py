import datetime as dt
import logging
import os
from pathlib import Path
from typing import Literal

from PIL import Image
from PySide6 import QtCore, QtGui, QtWidgets

from app.ui import qt_signals_handler
from app.utils import paths


class BookCreationPage(QtWidgets.QWidget):
    def __init__(
        self,
        parent,
        books_handler,
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
            QtGui.QIcon(os.path.join(self.icons_folder, "back_ico.png"))
        )
        self.exit_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.exit_b.clicked.connect(self.close_widget)

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
        self.edit_cover_b.clicked.connect(self.select_image)

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

        for index, shelf in enumerate(self.books_handler.books_shelfs.values()):
            shelf_cb = QtWidgets.QCheckBox(
                shelf.name if shelf.name else "[Untitled Shelf]"
            )
            self.shelfs_selection_cbs[shelf.id] = shelf_cb

        self.add_b = QtWidgets.QPushButton("Ajouter")
        self.add_b.clicked.connect(self.add_book)

        # Add the widgets
        self.container_widget_layout.addWidget(self.exit_b, 0, 0)
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
        self.main_layout.addWidget(self.scroll_area)

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

    def select_image(self):
        """Open a file selecter window for enable user to select an image"""
        self.selected_image = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Image",
            str(Path.home()),
            "Supported Formats (*.png *.jpeg);;PNG Images (*.png);;JPEG Images (*.jpeg)",
        )

        if self.selected_image[0]:
            final_image_infos = self.prepare_image(self.selected_image[0])

            if final_image_infos:
                self.cover_image = final_image_infos[0]
                self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def prepare_image(self, image_path: str | Path) -> tuple | None:
        """
        Convert <image_path> to PNG format, resize it and save it in the temporary directory and return the path
        """

        image_path = Path(image_path)
        if image_path.exists():
            with Image.open(image_path) as img:
                res = self.resize_image(img)
                res = self.convert_img_to_png(res)
                res_path = os.path.join(paths.TMP_DIR_PATH, "book_cover.png")
                res.save(res_path, "PNG")
                self.cover_image = res_path

            return (self.cover_image, res)

        else:
            self.logger.error(
                f"Unable to select cover image at {image_path.resolve()} : File not Found"
            )
            raise FileNotFoundError(
                f"Book cover image at {image_path.resolve()} not found !"
            )

    def resize_image(self, img):
        img_width, img_height = img.size
        resized_img = img.resize(
            (int(img_width * (170 / img_width)), int(img_height * (250 / img_height)))
        )

        return resized_img

    def convert_img_to_png(self, img: Image.Image):
        """
        Convert <img> to PNG format and return it
        """
        img_rgb = img.convert(mode="RGB")

        return img_rgb

    def close_widget(self):
        """
        If possible, switch to the previous page
        """

        if self.cover_image:
            self.logger.info("Deleting temporary book cover...")
            tmp_book_cover = Path(os.path.join(paths.TMP_DIR_PATH, "book_cover.png"))

            if tmp_book_cover.exists():
                tmp_book_cover.unlink()

            else:
                self.logger.warning("Temporary cover file not found !")

            self.qt_signals_handler.go_previous_page_sg.emit(True)

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

        books_infos["internal_id"] = str(
            dt.datetime.timestamp(dt.datetime.now())
        ).replace(".", "")

        if str(self.cover_image) != self.default_cover_img:
            self.final_cover_image = os.path.join(
                paths.BOOKS_COVERS_PATH,
                f"{books_infos['internal_id']}.png",
            )
            cover_img_path = Path(self.cover_image)

            if cover_img_path.exists():
                os.rename(
                    self.cover_image,
                    os.path.join(
                        paths.BOOKS_COVERS_PATH,
                        f"{books_infos['internal_id']}.png",
                    ),
                )
                # shutil.move(self.cover_image, paths.BOOKS_COVERS_PATH)

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

    def add_book(self):
        books_infos = self.get_book_infos()
        self.books_handler.create_book(**books_infos)
