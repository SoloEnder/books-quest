import logging
from PySide6 import QtWidgets
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
        self.langs_handler = langs_handler
        self.jump_to_page_lb.setText(self.langs_handler.tr("my_widgets_pagination_view.jump_to_page_lb"))
        self.nothing_page.set_label_text(self.langs_handler.tr("nothing_to_show_lb"))
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.general"),
            self.res_handler.get_res("assets.qss.widgets_pagination_view"), 
            widget=self, 
            logger=self.logger
            )
        
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
            self.qt_qignals_handler.notify_sg.emit("error", "Page not found", self.langs_handler.tr("my_widgets_pagination_view.invalid_page_index_msg"), "")
        
