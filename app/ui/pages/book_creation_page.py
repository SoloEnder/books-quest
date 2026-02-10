
import io
import shutil
import logging
import datetime as dt
from PIL import Image
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from app.utils import paths

class BookCreationPage(QtWidgets.QWidget):

    def __init__(self, parent: None, books_handler):
        super().__init__(parent)
        self.books_handler = books_handler
        self.logger = logging.getLogger(__name__)
        self.icons_folder = paths.get_abspath("app/assets/icons")

        self.basic_book_infos = {
            "titre":"Titre : ",
            "author":"Auteur : ",
            "edition":"Edition : ",
            "summary": "Résumé : ",
            "tot_pages":"Pages totales : ",
            "alr_read_pages":"Pages lues : "
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

        #Exit Widget
        self.exit_b = QtWidgets.QPushButton("Fermer")
        self.exit_b.setIcon(QtGui.QIcon(str(Path.joinpath(self.icons_folder, "close_ico.png"))))
        self.exit_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.exit_b.clicked.connect(self.close)

        # Cover widgets
        self.cover_image = paths.get_abspath("app/assets/default_book_cover.png")
        self.book_cover_lb = QtWidgets.QLabel()
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))
        self.edit_cover_b = QtWidgets.QPushButton("Changer la couverture")
        self.edit_cover_b.setIcon(QtGui.QIcon("app/assets/icons/edit_ico.png"))
        self.edit_cover_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.edit_cover_b.clicked.connect(self.select_image)

        # Book infos widgets
        row = 3
        for key, value, in self.basic_book_infos.items():
            lb = QtWidgets.QLabel(value)
            ew = QtWidgets.QLineEdit() if key != "summary" else QtWidgets.QTextEdit()

            if key == "summary":
                lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            ew.setMaximumWidth(300)
            self.container_widget_layout.addWidget(lb, row, 0)
            self.container_widget_layout.addWidget(ew, row, 1)
            self.basic_book_info_ew[key] = ew
            row += 1

        #Book statut widgets
        self.book_statut_widgets_infos = ("En cours", "Terminé", "Pas encore lut")
        self.book_statut_widgets = {}

        for info in self.book_statut_widgets_infos:
            self.book_statut_rb = QtWidgets.QRadioButton(info)
            self.book_statut_widgets[info] = self.book_statut_rb

        #Shelfs widgets
        self.shelfs_selection_lb = QtWidgets.QLabel("Etageres : ")
        self.shelfs_selection_cbs = {}
        self.shelfs_selection_widget = QtWidgets.QWidget(self)
        self.shelfs_selection_layout = QtWidgets.QVBoxLayout(self.shelfs_selection_widget)
        self.shelfs_selection_widget.setLayout(self.shelfs_selection_layout)
        self.shelfs_selection_scroll_area = QtWidgets.QScrollArea(self)
        self.shelfs_selection_scroll_area.setMaximumWidth(300)
        self.shelfs_selection_scroll_area.setMinimumHeight(450)
        self.shelfs_selection_scroll_area.setWidgetResizable(True)
        self.shelfs_selection_scroll_area.setWidget(self.shelfs_selection_widget)

        for index, shelf in enumerate(self.books_handler.books_shelfs.values()):

            if shelf.name != "Tout les livres":
                shelf_cb = QtWidgets.QCheckBox(shelf.name)
                self.shelfs_selection_cbs[shelf.id] = shelf_cb
                self.shelfs_selection_layout.addWidget(shelf_cb, index)

        self.add_b = QtWidgets.QPushButton("Ajouter")
        self.add_b.clicked.connect(self.add_book)

        # Add the widgets
        self.container_widget_layout.addWidget(self.exit_b, 0, 0)
        self.container_widget_layout.addWidget(self.book_cover_lb, 1, 0)
        self.container_widget_layout.addWidget(self.edit_cover_b, 2, 0)
        self.container_widget_layout.addWidget(self.shelfs_selection_lb, self.container_widget_layout.rowCount()+1, 0)
        self.container_widget_layout.addWidget(self.shelfs_selection_scroll_area, self.container_widget_layout.rowCount()+1, 0)
        self.container_widget_layout.addWidget(self.add_b, self.container_widget_layout.rowCount()+1, 0)
        self.main_layout.addWidget(self.scroll_area)

    def set_default_cover(self):
        self.cover_image = paths.get_abspath("app/assets/default_book_cover.png")
        self.book_cover_lb.setPixmap(QtGui.QPixmap(self.cover_image))

    def select_image(self):
        self.selected_image = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", str(Path.home()), "Supported Formats (*.png *.jpeg);;PNG Images (*.png);;JPEG Images (*.jpeg)")

        if self.selected_image[0]:
            self.cover_image = self.selected_image[0]
            self.book_cover_lb.setPixmap(QtGui.QPixmap(self.prepare_image(self.cover_image)[0]))

    def prepare_image(self, image_path: str|Path):
        """
        Convert <image_path> to PNG format, resize it and save it in the temporary directory and return the path
        """

        image_path = Path(image_path)

        with Image.open(image_path) as img:
            res = self.resize_image(img)
            res = self.convert_img_to_png(res)
            self.cover_image = paths.get_abspath("app/tmp/book_cover.png")
            res.save(self.cover_image, "PNG")

        return (self.cover_image, res)

    def resize_image(self, img):
        img_width, img_height = img.size
        resized_img = img.resize((int(img_width/(img_width/140)), int(img_height/(img_height/200))))

        return resized_img
    
    def convert_img_to_png(self, img: Image.Image):
        """
        Convert <img> to PNG format and return it
        """
        img_rgb = img.convert(mode='RGB')

        return img_rgb
    
    def close(self):
        """
        If possible, switch to the previous page
        """

        self.logger.info("Book creation canceled !")

        if self.cover_image:
            self.logger.info("Deleting temporary book cover...")
            tmp_book_cover = Path(paths.get_abspath("app/tmp/book_cover.png"))

            if tmp_book_cover.exists():
                tmp_book_cover.unlink()

            else:
                self.logger.warning("Temporary cover file not found !")

            self.set_default_cover()

        parent = self.parent()

        if parent:

            if parent.history and len(parent.history) > 1:
                parent.switch_page(parent.history[1])
            
            else:
                parent.switch_to_default_page()

    def get_book_infos(self):
        books_infos = {}

        for key, w in self.basic_book_info_ew.items():

            if type(w) == QtWidgets.QLineEdit:
                text = w.text()

                if text:
                    books_infos[key] = text

            elif type(w) == QtWidgets.QTextEdit:
                text = w.toPlainText()

                if text:
                    books_infos[key] = text

        books_infos["internal_id"] = str(dt.datetime.timestamp(dt.datetime.now())).replace(".", "")

        if self.cover_image != str(paths.get_abspath("app/assets/default_book_cover.png")):
            cover_img_path = Path(self.cover_image)

            if cover_img_path.exists():
                #cover_img_path.rename(paths.get_abspath(f"app/data/books/{books_infos['internal_id']}.png"))
                shutil.move(self.cover_image, paths.get_abspath(f"app/data/books/books_covers/{books_infos['internal_id']}.png"))
                self.cover_image = paths.get_abspath(f"app/data/books/books_covers/{books_infos['internal_id']}.png")

            books_infos["cover_img_path"] = str(paths.get_abspath(f"app/data/books/books_covers/{books_infos['internal_id']}.png"))

        books_infos["shelfs_ids"] = []
        for shelf_id, shelf_selection_cbs in self.shelfs_selection_cbs.items():

            if shelf_selection_cbs.isChecked():
                books_infos["shelfs_ids"].append(shelf_id)

        return books_infos        

    def add_book(self):
        books_infos = self.get_book_infos()
        self.books_handler.create_book(**books_infos)
