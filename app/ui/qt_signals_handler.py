from PySide6 import QtCore, QtGui


class QtSignalsHandler(QtCore.QObject):
    apply_settings_sg = QtCore.Signal()
    refresh_ui_sg = QtCore.Signal()
    refresh_page_sg = QtCore.Signal(str, dict)
    refresh_current_page_sg = QtCore.Signal()
    switch_page_sg = QtCore.Signal(str, bool, dict)
    close_page_sg = QtCore.Signal()
    notify_sg = QtCore.Signal(str, str, str, str)
    add_action_sg = QtCore.Signal(list[QtGui.QAction])
    edit_progress_msg = QtCore.Signal(str)
    show_about_sg = QtCore.Signal(bool)
    get_app_infos_sg = QtCore.Signal(
        dict
    )  # Get the app infos by adding them to the dictionnary argument

    def __init__(self):
        super().__init__()
