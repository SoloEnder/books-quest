from PySide6 import QtCore


class QtSignalsHandler(QtCore.QObject):
    switch_page_sg = QtCore.Signal(str, bool, dict)
    go_previous_page_sg = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()
