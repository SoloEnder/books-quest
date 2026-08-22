from PySide6 import QtCore, QtGui, QtWidgets

from app.src.book_sys import Book, Shelf


class QtSignalsHandler(QtCore.QObject):
    apply_settings_sg = QtCore.Signal()
    refresh_ui_sg = QtCore.Signal()
    refresh_page_sg = QtCore.Signal(str, dict)
    refresh_current_page_sg = QtCore.Signal()
    switch_page_sg = QtCore.Signal(str, bool, dict)
    close_page_sg = QtCore.Signal()
    notify_sg = QtCore.Signal(str, str, str, str)
    edit_progress_msg = QtCore.Signal(str)
    show_about_sg = QtCore.Signal(bool)
    write_version_on_widget_sg = QtCore.Signal(
        QtWidgets.QWidget
    )  # Write the app current version on an widget that support `setText` method
    check_for_updates_sg = QtCore.Signal(
        bool
    )  # Checks for update. First argument indicates whether to show a pop-up when app is up to date
    # ---- Signal emited when user add/edit an object in the library. First parameter is the object ID
    book_added_sg = QtCore.Signal(str)
    book_edited_sg = QtCore.Signal(str)
    book_removed_sg = QtCore.Signal(str)
    shelf_added_sg = QtCore.Signal(str)
    shelf_edited_sg = QtCore.Signal(str)
    shelf_removed_sg = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
