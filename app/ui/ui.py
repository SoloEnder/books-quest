
import customtkinter as ctk
from app.ui import menu_bar
from app.ui.tabs import books_tab


class UI(ctk.CTk):

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.menu_bar = menu_bar.MenuBar(self)
        self.menu_bar.add_tab(label="Books", tab_object=books_tab.BooksTab(self))
        self.menu_bar.draw_widgets()
        self.menu_bar.switch_tab("Books")
        self.menu_bar.draw_tab()
        self.menu_bar.grid(row=0, column=0, sticky="wns")