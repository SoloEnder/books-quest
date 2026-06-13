import logging
from PySide6 import QtWidgets, QtGui
import widgets_pagination_view

from app.utils import utils_funcs
from app.ui import qt_signals_handler
from app.src import langs_handler
from app.src import resources_handler
       
class MyWidgetsPaginationView(widgets_pagination_view.WidgetsPaginationView):        
        
    def __init__(
        self,
        res_handler: resources_handler.RessourcesHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler, 
        langs_handler: langs_handler.LangsHandler,
        parent: QtWidgets.QWidget|None, 
        max_loadables_pages_count: int, 
        widgets_by_page_count: int, 
        widgets: widgets_pagination_view.InPageWidgetsList,
        **config,
        ):
        self.langs_handler = langs_handler
        self.nothing_to_show_page = NothingToShowPage(None, self.my_tr("shared.labels.nothing_to_show", False))
        super().__init__(
            parent=parent, 
            max_loadables_pages_count=max_loadables_pages_count, 
            widgets_by_page_count=widgets_by_page_count,
            widgets=widgets,
            **config
        )
        self.logger = logging.getLogger(__name__+"WidgetsPaginationView")
        self.res_handler = res_handler
        self.qt_qignals_handler = qt_signals_handler
        self.redundant_lang_path = "my_widgets_pagination_view"
        self.jump_to_page_lb.setText(self.my_tr(".labels.jump_to_page"))
        self.main_lyt.addWidget(self.nothing_to_show_page, 0, 0)
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.general"),
            self.res_handler.get_res("assets.qss.widgets_pagination_view"), 
            widget=self, 
            logger=self.logger
            )
        
    def generate_pages(self):
        super().generate_pages()
        if self.widgets:
            self.nothing_to_show_page.setVisible(False)
            
        else:
            self.nothing_to_show_page.setVisible(True)
            
    def delete_widget(self, widget: widgets_pagination_view.InPageWidget):
        super().delete_widget(widget)
        if self.widgets:
            self.nothing_to_show_page.setVisible(False)
            
        else:
            self.nothing_to_show_page.setVisible(True)
        
    def _generate_pages_buttons(self, pages_indexes: list | tuple):
        super()._generate_pages_buttons(pages_indexes)
        
        if len(self.pages_numbers_lyt_widgets) > 1:
            last_button = self.pages_numbers_lyt_widgets[-1]
            last_button.setText(f". . . {last_button.text()}")
            last_button.setObjectName("last_page_b")
            
    def _jump_to_page(self, given_input):
        
        try:
            super()._jump_to_page(given_input)
            
        except ValueError:
            self.qt_qignals_handler.notify_sg.emit("error", "Page not found", self.tr("my_widgets_pagination_view.notifications.invalid_page_index"), "")
            
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
        
class NothingToShowPage(QtWidgets.QWidget):
    
    def __init__(self, parent: QtWidgets.QWidget|None, text):
        super().__init__(parent)
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)
        self.label = QtWidgets.QLabel(text)
        self.label.setProperty("role", "nothing_to_show_lb")
        self.main_lyt.addWidget(self.label, 0, 0, QtGui.Qt.AlignmentFlag.AlignCenter)
        
    def edit_label_text(self, new_text: str):
        self.label.setText(new_text)
