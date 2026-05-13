import datetime as dt
import logging
import os
from PySide6 import QtCore, QtGui, QtWidgets
import typing

from app.utils import utils_funcs
from app.utils import my_exceptions

from app.src import book_sys
from app.ui import qt_signals_handler
from app.utils import paths

def dynamic_pages_switching(func):
    """
    Wrapper of the 'PagesWidgetsHandler.switch_to_page' method\n
    When the numbers of loaded pages exceed 'PagesWidgetsHandler.max_loadables_pages_count', all exceeding pages are automaticaly unloaded\n
    The use of this wrapper may improves the performances
    """

    def wrapper(self: PagesWidgetsHandler, page_index):

        func(self, page_index)
        exceeding_pages = self.loaded_pages[:-self.max_loadables_pages_count]

        if exceeding_pages:
            self.logger.debug(f"Unloading {len(exceeding_pages)} exceedings pages, indexes={[exceeding_page.virtual_index for exceeding_page in exceeding_pages]}")
            
            for exceeding_page in exceeding_pages:
                self.unload_page(exceeding_page)

    return wrapper

def dynamic_pages_loader(func):

    def wrapper(self: PagesWidgetsHandler):
        func(self, self.pages_data[:2])

    return wrapper
       
class PagesWidgetsHandler(QtWidgets.QWidget):        
        
    def __init__(self, parent: QtWidgets.QWidget|None, qt_signals_handler,  max_loadables_pages_count: int, widgets_by_page_count: int, widgets: list[InPageWidget],):
        super().__init__(parent)

        #Assigning arguments to attr
        self.qt_signals_handler = qt_signals_handler
        self.widgets_by_page_count = widgets_by_page_count
        self.max_loadables_pages_count = max_loadables_pages_count
        self.widgets = widgets
        
        #Setup logger
        self.logger = logging.getLogger(__name__+":PagesWidgetsHandler")
        
        self.pages_data = []
        self.pages_virtual_row = []
        self.loaded_pages = []
        self.pages_switch_history = []
        
        self.setObjectName("pages_widgets_handler")
        self.main_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.main_lyt)
        
        #The stacked widget which handle the widgets
        self.pages_widgets_sw = QtWidgets.QStackedWidget(self)
        
        #Widgets for pages numbers buttons
        self.pages_numbers_widget = QtWidgets.QWidget(self)
        self.pages_numbers_widget_lyt = QtWidgets.QHBoxLayout(self.pages_numbers_widget)
        self.pages_numbers_widget.setLayout(self.pages_numbers_widget_lyt)
        self.pages_numbers_buttons = []
        
        self.main_lyt.addWidget(self.pages_widgets_sw, 0, 0)
        self.main_lyt.addWidget(self.pages_numbers_widget, 1, 0)
        
        self.nothing_to_show_widget = QtWidgets.QWidget()
        self.nothing_to_show_widget_lyt = QtWidgets.QHBoxLayout()
        self.nothing_to_show_widget.setLayout(self.nothing_to_show_widget_lyt)
        self.nothing_to_show_lb = QtWidgets.QLabel(self)
        self.nothing_to_show_lb.setText("Il n'y a rien ici")
        self.nothing_to_show_lb.setProperty("role", "nothing_to_show_lb")
        self.nothing_to_show_widget_lyt.addWidget(self.nothing_to_show_lb, QtCore.Qt.AlignmentFlag.AlignCenter)
        self.pages_widgets_sw.addWidget(self.nothing_to_show_widget)
        utils_funcs.load_and_set_ss(os.path.join(paths.QSS_FILES_PATH, "pages_widgets_handler.qss"), widget=self, logger=self.logger)
        
    def _fill_virt_row(self):
        """
        Append 'None' to the 'pages_virtual_row' attribute for every page_data found in the 'pages_data' attribute\n
        All existing values in 'pages_virtual_row' will be erased
        """
        
        self.pages_virtual_row.clear()
        
        for page_data in self.pages_data:
            self.pages_virtual_row.append(None)
        
        
    def set_widgets(self, widgets: list[InPageWidget]):
        """
        Set the attribute 'widgets' to 'widgets'
        """
        self.widgets = widgets
        
    def delete_widget(self, widget: InPageWidget, destroy: bool=True):
        page_destroyed = False
            
        for page in self.loaded_pages.copy():
            self.unload_page(page)
            
        if isinstance(widget.index, int):
            self.logger.debug(f"Destroying widget with virtual index={widget.index} !")
            del self.widgets[widget.index]
            
            for widget in self.widgets[widget.index:]:
                
                if isinstance(widget.index, int) and widget.index >= 0:
                    widget.set_index(widget.index-1)
                    
                else:
                    raise my_exceptions.InvalidWidgetIndexError(widget)
                    
            self._shift_slice(-1, -1, "RIGHT")
            
        if self.pages_data[-1][1][0] == self.pages_data[-1][1][1]:
            page_destroyed = True
            self.logger.debug(f"Removing page with virtual index={self.pages_data[-1][0]}")
            self.remove_page(self.pages_data[-1][0], False)
            self._generate_pages_buttons([x for x in range(len(self.pages_data[:5]))])
            
        self.logger.debug(f"{self.pages_switch_history}")
        last_i = self.pages_switch_history[0]
        
        if page_destroyed:
            
            for i in self.pages_switch_history:
                
                if i != last_i:
                    self.switch_to_page(i)
                    break
        else:
            self.switch_to_page(self.pages_switch_history[0])
            
    def remove_page(self, page_index, re_setup: bool=True):
        """
        Removes the page and his data at 'page_index' in the 'virtual_row' attribute
        
        Args:
        - page_index: the page index
        - re_setup: Wether or not call the 'setup_pages_slices' method after deleting the page. You should call it by yourself otherwise
        """
        
        self.unload_page_with_index(page_index)
        del self.pages_data[page_index]
        del self.pages_virtual_row[page_index]
        
        if re_setup:
            self.setup_pages_slices()
            
    def _shift_slice(self, page_data_index: int, shift_value: int, shift_side: typing.Literal["LEFT", "RIGHT"]):
        
        if shift_side == "RIGHT":
            pages_data = self.pages_data[page_data_index]
            pages_data[1] = (pages_data[1][0], pages_data[1][1]+shift_value)
            
        elif shift_side == "LEFT":
            pages_data = self.pages_data[page_data_index]
            pages_data[1] = (pages_data[1][0]+shift_value, pages_data[1][1])
            
        else:
            raise ValueError(f"Unkown value given for argument 'shift_side' : {shift_side}. Valid value : 'RIGHT', 'LEFT'")
        
    def setup_pages_slices(self):
        current_page_index = 0
        slice_start = 0
        slice_end = 0
        page_data = []
        widgets_count = len(self.widgets)
        self.pages_virtual_row.clear()
        
        for index, widget in enumerate(self.widgets):
            widget.set_index(index)
            widget.set_pages_widgets_handler(self)
            
            if (index+1) % self.widgets_by_page_count == 0:
                slice_start = slice_end
                slice_end = index+1
                page_data = [current_page_index, (slice_start, slice_end)]
                current_page_index += 1
                self.pages_data.append(page_data.copy())
                self.pages_virtual_row.append(None)
                
        if slice_end != widgets_count:
            slice_start = slice_end
            slice_end = widgets_count
            page_data = [current_page_index, (slice_start, slice_end)]
            self.pages_data.append(page_data.copy())
            self.pages_virtual_row.append(None)
        
    def generate_pages(self):
        """
        Generate all pages widgets using the attribute 'pages_data'
        You should call the 'setup_pages_slices' method once before call this method
        """
        
        self.logger.debug(f"Generating {self.max_loadables_pages_count} pages...")
        
        for page_data in self.pages_data[:self.max_loadables_pages_count]:
            self.new_page(page_data)
        
        pages_data_count = len(self.pages_data)
        
        if pages_data_count > 5:
            self._generate_pages_buttons([0, 1, 2, 3, 4, pages_data_count-1])
            
        else:
            self._generate_pages_buttons([i for i in range(pages_data_count)])
            
        self.switch_to_page(0)
        
    def _generate_pages_buttons(self, pages_indexes: list|tuple, format_last_button: bool=True):
        """
        Generates buttons for pages switching\n
        All previous button in the layout will be cleared !
        
        pages_indexes: the pages indexes used for pages switching (Note that the displayed index will be the given index+1)
        format_last_button: if True, a specific style will be applied to the last button
        """
        
        for widget in self.pages_numbers_buttons:
            self.pages_numbers_widget_lyt.removeWidget(widget)
            widget.deleteLater()
            
        self.pages_numbers_buttons.clear()
        
        for index in pages_indexes:
            button = QtWidgets.QPushButton(f"{index+1}")
            button.clicked.connect(lambda qt_arg, i=index: self.switch_to_page(i))
            
            if format_last_button and index == pages_indexes[-1]:
                button.setText(f". . .{index+1}")
                button.setObjectName("last_page_b")
                
            self.pages_numbers_widget_lyt.addWidget(button)
            self.pages_numbers_buttons.append(button)
        
    def get_widgets_with_slice(self, slice: tuple[int, int]) -> list[InPageWidget]:
        """
        Get and return all the widget which are contained inside 'slice'
        """
        return self.widgets[slice[0]:slice[1]]
        
    def new_page(self, page_data: list):
        """
        Creates and add to the stacked widgets a new 'page_data' object\n
        Equivalent to : 'self.add_page(self.create_pages(page_data))'
        """
        
        new_page = self.create_page(page_data)
        self.add_page(new_page)
        
    def create_page(self, page_data: list):
        """
        Create and return a new 'Page' object and return it        
        """
        
        return Page(self, self.qt_signals_handler, page_data[0], page_data[1])
    
    def add_page(self, page: Page):
        """
        Add 'page' to the stacked widgets
        """
        self.logger.debug(f"Adding page with index={page.virtual_index}")
        self.pages_widgets_sw.addWidget(page)
        self.pages_virtual_row[page.virtual_index] = page
        self.loaded_pages.append(page)
        
    @dynamic_pages_switching
    def switch_to_page(self, index: int, make_page: bool=True):
        """
        Set the page displayed to the one's at 'index' int the 'pages_virtual_row' attribute
        
        Args:
        - index (int): the index of the page
        - make_page (bool, default to True): whether or not create the destination page if this is not the case
        
        Raises:
        - PagesNotLoadedError: if the destination page is not crated yet and make_page is equal to False
        """
        
        self.logger.debug(f"Switching to page with index={index}")
        dest_page = self.pages_virtual_row[index]
        
        if dest_page:
            self.pages_widgets_sw.addWidget(dest_page)
            self.pages_widgets_sw.setCurrentWidget(dest_page)
            self.pages_switch_history.insert(0, dest_page.virtual_index)
            
        else:
            if make_page:
                dest_page = self.create_page(self.pages_data[index])
                self.add_page(dest_page)
                self.pages_widgets_sw.setCurrentWidget(dest_page)
                self.pages_switch_history.insert(0, dest_page.virtual_index)
                
            else:
                raise my_exceptions.PageNotLoadedError(index)
        
    def unload_page_with_index(self, index: int):
        """
        Unloads the page at 'index' in the 'virtual_row' attribute\n
        Equivalent to call 'self.unload_page(self.virtual_row[index])'
        """
        
        page = self.pages_virtual_row[index]
        
        if page == None:
            my_exceptions.PageNotLoadedError(index)
            
        else:
            self.unload_page(page)
        
    def unload_page(self, page: Page):
        """
        Removes 'page' from the widget which display them, and destroy it
        """
        
        try:
            self.loaded_pages.remove(page)
            
        except ValueError:
            raise my_exceptions.PageNotLoadedError(page.virtual_index)
        
        self.pages_widgets_sw.removeWidget(page)
        self.pages_virtual_row[page.virtual_index] = None
        page.deleteLater()
                      
class Page(QtWidgets.QWidget):
    def __init__(
        self,
        pages_widgets_handler: PagesWidgetsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
        virtual_index: int,
        widgets_slice: tuple[int, int]
    ):
        super().__init__(pages_widgets_handler)
        self.logger = logging.getLogger(__name__)
        self.qt_signals_handler = qt_signals_handler
        self.pages_widgets_handler = pages_widgets_handler
        self.widgets_slice = widgets_slice
        self.virtual_index = virtual_index

        self.setProperty("role", "page")
        self.main_layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.main_layout)

        self.widgets_container = QtWidgets.QWidget(self)
        self.widgets_container_layout = QtWidgets.QVBoxLayout(self.widgets_container)
        self.widgets_container.setLayout(self.widgets_container_layout)
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.widgets_container)

        self.main_layout.addWidget(self.scroll_area, 3, 0)
        self.place_widgets()

        #if self.index == 0:
        #    self.default_shelf_widget = DefaultShelfWidget(
        #        self.books_handler.default_shelf,
        #        self.books_handler,
        #        self.qt_signals_handler,
        #    )

        #    self.shelfs_container_layout.addWidget(
        #        self.default_shelf_widget, QtCore.Qt.AlignmentFlag.AlignTop
        #    )
        
    def place_widgets(self):
        
        for widget in self.pages_widgets_handler.get_widgets_with_slice(self.widgets_slice):
            self.widgets_container_layout.addWidget(widget)
            
    def deleteLater(self):
        for widget in self.pages_widgets_handler.get_widgets_with_slice(self.widgets_slice):
            widget.setParent(None)
        
        return super().deleteLater()
        
class InPageWidget(QtWidgets.QWidget):
    
    def __init__(self, pages_widgets_handler: PagesWidgetsHandler|None, index: int|None):
        super().__init__(None)
        self.index = index
        self.pages_widgets_handler = pages_widgets_handler
        
    def set_pages_widgets_handler(self, pages_widgets_handler: PagesWidgetsHandler):
        """
        Setter of attribute 'pages_widgets_handler'
        """
        
        self.pages_widgets_handler = pages_widgets_handler
        
    def set_index(self, index: int):
        """
        Setter of attribute 'index'
        """
        self.index = index
        
