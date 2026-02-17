from PySide6 import QtCore


class MySignalsHandler(QtCore.QObject):
    switch_page_signal = QtCore.Signal(str, bool, dict)
    go_previous_page_sg = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()
