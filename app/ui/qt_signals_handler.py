from PySide6 import QtCore, QtGui


class QtSignalsHandler(QtCore.QObject):
    refresh_ui_sg = QtCore.Signal()
    switch_page_sg = QtCore.Signal(str, bool, dict)
    close_page_sg = QtCore.Signal()
    notify_sg = QtCore.Signal(str, str, str, str)
    add_action_sg = QtCore.Signal(list[QtGui.QAction])
    edit_progress_msg = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
