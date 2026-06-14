from PySide6 import QtCore, QtWidgets


class NotificationService:
    def __init__(self, widget_parent: QtWidgets.QWidget, langs_handler):
        self.widget_parent = widget_parent
        self.langs_handler = langs_handler
        self.redundant_lang_path = "notifications_service"
        self.default_warning_infos = {
            "title": self.langs_handler.tr(".notifications.error.title"),
            "msg": self.langs_handler.tr(".notifications.error.msg"),
        }
        self.default_information_infos = {
            "title": self.langs_handler.tr(".notifications.info.title")
        }

    @QtCore.Slot(str, str, str, str)
    def notify(
        self, lvl: str | None, title: str | None, msg: str | None, details: str | None
    ):

        if lvl == "error":
            self.show_error(title, msg)

        if lvl == "info":
            self.show_info(title, msg)  # type: ignore

    def show_error(self, title: str | None, msg: str | None):
        QtWidgets.QMessageBox.warning(
            self.widget_parent,
            title if title else self.default_warning_infos["title"],
            msg if msg else self.default_warning_infos["msg"],
        )

    def show_info(self, title: str | None, msg: str):
        QtWidgets.QMessageBox.information(
            self.widget_parent,
            title if title else self.default_information_infos["title"],
            msg,
        )
