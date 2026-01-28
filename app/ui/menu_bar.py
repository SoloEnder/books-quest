
import logging

from app.ui import my_widgets


import customtkinter as ctk

class MenuBar(my_widgets.MyFrame):

    def __init__(self, master, events_handler, **kwargs):
        self.logger = logging.getLogger(__name__)
        super().__init__(master, **kwargs)
        self.events_handler = events_handler
        self.tabs = {}
        self.current_tab = None

    def add_tab(self, label: str, tab_object: ctk.CTkFrame | ctk.CTkScrollableFrame):
        self.tabs[label] = tab_object
        self.logger.debug(f"Tab {label} added to the menu bar")

    def draw_widgets(self):

        for index, label in enumerate(self.tabs.keys()):
            tab_b = ctk.CTkButton(self, text=label, command=lambda tab_name=label: self.switch_tab)
            tab_b.grid(row=index, column=0)

    def switch_tab(self, tab_name: str):

        if self.current_tab:
            self.current_tab.grid_remove()

        self.current_tab = self.tabs[tab_name]
        self.current_tab.grid(row=0, column=1, sticky="nsew")
        self.logger.info(f"Switched to tab {tab_name}")

    def draw_tab(self, tab_name: str|None=None):
        if tab_name:
            self.switch_tab(tab_name)

        if self.current_tab:
            self.current_tab.draw_widgets()
