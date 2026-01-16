
import customtkinter as ctk
from app.ui import menu_bar
from app.ui.screens import books_page
from app.utils import paths


class UI(ctk.CTk):

    def __init__(self, app, books_handler, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.books_handler = books_handler
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        ctk.FontManager.load_font(str(paths.get_absfilepath("assets", "icons.ttf")))
        self.menu_bar = menu_bar.MenuBar(self)
        self.menu_bar.add_tab(label="Books", tab_object=books_page.BooksTab(self, self.books_handler))
        self.menu_bar.draw_widgets()
        self.menu_bar.switch_tab("Books")
        self.menu_bar.draw_tab()
        self.menu_bar.grid(row=0, column=0, sticky="wns")

