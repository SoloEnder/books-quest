
from PySide6 import QtCore, QtWidgets

class NotificationService:
    
    def __init__(self, widgets_parent: QtWidgets.QWidget):
        self.widgets_parent = widgets_parent
        self.default_warning_infos = {"title":"Avertissement", "msg":"Une erreur est survenue, veuillez réessayer"}
        self.default_information_infos = {"title":"Information"}
    
    @QtCore.Slot(str, str, str, str)
    def notify(self, lvl: str|None, title: str|None, msg: str|None, details: str|None):
        
        if lvl == "error":
            self.show_error(title, msg)
            
        if lvl == "info":
            self.show_info(title, msg) # type: ignore

    def show_error(self, title: str|None, msg: str|None):
        QtWidgets.QMessageBox.warning(
            self.widgets_parent, 
            title if title else self.default_warning_infos["title"], 
            msg if msg else self.default_warning_infos["msg"]
            )
        
    def show_info(self, title: str|None, msg: str):
        QtWidgets.QMessageBox.information(
            self.widgets_parent, 
            title if title else self.default_information_infos["title"], 
            msg,
            )
        
        