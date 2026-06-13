
from PySide6 import QtCore, QtWidgets

class NotificationService:
    
    def __init__(
        self, 
        widget_parent: QtWidgets.QWidget, 
        langs_handler
        ):
        self.widget_parent = widget_parent
        self.langs_handler = langs_handler
        self.redundant_lang_path = "notifications_service"
        self.default_warning_infos = {
            "title":self.my_tr(".notifications.error.title"), 
            "msg":self.my_tr(".notifications.error.msg")}
        self.default_information_infos = {"title":self.my_tr(".notifications.info.title")}
    
    @QtCore.Slot(str, str, str, str)
    def notify(self, lvl: str|None, title: str|None, msg: str|None, details: str|None):
        
        if lvl == "error":
            self.show_error(title, msg)
            
        if lvl == "info":
            self.show_info(title, msg) # type: ignore

    def show_error(self, title: str|None, msg: str|None):
        QtWidgets.QMessageBox.warning(
            self.widget_parent, 
            title if title else self.default_warning_infos["title"], 
            msg if msg else self.default_warning_infos["msg"]
            )
        
    def show_info(self, title: str|None, msg: str):
        QtWidgets.QMessageBox.information(
            self.widget_parent, 
            title if title else self.default_information_infos["title"], 
            msg,
            )
        
    def my_tr(self, lang_path: str, fill: bool=True, **kwargs) -> str:
        """Do the same as the 'langs_handler.tr()' attribute, but auto-complete the first part of the 'lang_path' by the value of the 'rebondant_lang_path' attr.\n
        Note that your shortcut lang_path must start by '.' for the auto completion to work.
        
        Parameters
        ----------
        fill (bool=True): specifies wheter or not to fill the begining of the lang_path
        **kwargs: the additionnal arguments for the translation text
        
        Returns
        -------
        str: the translation
        
        Example:
        --------
        you can pass the lang_path '.buttons.do_something' instead of 'main_pages.page_name.buttons.do_something'\n
        if the value of the 'redundant_lang_path' is 'main_pages.page_name'
        """
        
        if fill and hasattr(self, "redundant_lang_path") and lang_path.startswith("."):
            return self.langs_handler.tr(self.redundant_lang_path+lang_path, **kwargs)
        
        else:
            return self.langs_handler.tr(lang_path, **kwargs)
        
        