
import logging
import datetime as dt
from tkinter import ttk
from typing import Literal
import customtkinter as ctk

from app.ui import my_widgets

class ShelfCreationFrame(my_widgets.MyScrollableFrame):

    def __init__(self, master, books_handler, events_handler, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.events_handler = events_handler
        self.events_handler.add_listener("System.Ui.ShelfFrameCreated", self.manage_shelf_creation_loading_tp)

    def draw_widgets(self):
        self.manage_shelf_creation_loading_tp("create")
        self.error_b = my_widgets.ErrorButton(self, "Erreur", "Ce titre est réservé au système, désolé.")
        self.error_b.draw_widgets()
        self.title_lb = ctk.CTkLabel(self, text="Titre")
        self.title_lb.grid(row=0, column=0, sticky="w ")
        self.title_e = ctk.CTkEntry(self)
        self.title_e.grid(row=1, column=0, sticky="w")
        self.select_books_lb = ctk.CTkLabel(self, text="Books")
        self.select_books_lb.grid(row=2, column=0)
        self.books_treeview = ttk.Treeview(self, columns=("book_title", "book_authors", "book_edition"))
        self.books_treeview.heading("#0", text="ID")
        self.books_treeview.heading("book_title", text="Titre")
        self.books_treeview.heading("book_authors", text="Authors")
        self.books_treeview.heading("book_edition", text="Edition")
        
        for book_obj in self.books_handler.books.values():
            self.books_treeview.insert("", "end", text=book_obj.internal_id, values=(book_obj.title, book_obj.authors, book_obj.edition))

        self.books_treeview.grid(row=3, column=0)
        self.validate_b = ctk.CTkButton(self, text="Ajouter", command=self.create_book_shelf)
        self.validate_b.grid(row=0, column=1, rowspan=2)

    def create_book_shelf(self):
        self.manage_shelf_creation_loading_tp(event=None, action="show")
        book_shelf_infos = self.get_infos()

        if book_shelf_infos:
            self.events_handler.raise_event("System.Books.ShelfCreationRequest", shelf_name=book_shelf_infos["shelf_name"], shelf_books=book_shelf_infos["shelf_books"], shelf_id=book_shelf_infos["shelf_id"])
            self.manage_shelf_creation_loading_tp(event=None, action="create")
            self.manage_shelf_creation_loading_tp(event=None, action="show")

    def manage_shelf_creation_loading_tp(self, event, action: Literal["create", "show", "hide", "destroy"]="destroy", **kwargs):
        """
        Show/Hide/Create or Destroy the loading creation toplevel window

        event: used if the function is called by the events handler. set it to None if you call this func manually
        action (str): the action ('create', 'show', 'hide' or 'destroy') 
        """

        if action == "create":
            self.shelf_creation_loading_tp = ctk.CTkToplevel()
            self.shelf_creation_loading_tp.title("Création de l'étagère...")
            self.shelf_creation_loading_tp.withdraw()
            self.shelf_creation_loading_lb = ctk.CTkLabel(self.shelf_creation_loading_tp, text="Création de votre étagère...")
            self.shelf_creation_loading_lb.grid(row=0, column=0)
            self.shelf_creation_loading_pb = ctk.CTkProgressBar(self.shelf_creation_loading_tp, mode="indeterminate")
            self.shelf_creation_loading_pb.grid(row=1, column=0)

        elif action == "show":

            if hasattr(self, "shelf_creation_loading_tp"):
                self.shelf_creation_loading_pb.start()
                self.shelf_creation_loading_tp.deiconify()

        elif action == "hide":

            if hasattr(self, "shelf_creation_loading_tp"):
                self.shelf_creation_loading_pb.stop()
                self.shelf_creation_loading_tp.withdraw()

        elif action == "destroy":

            if hasattr(self, "shelf_creation_loading_tp"):
                self.shelf_creation_loading_tp.destroy()

        else:
            self.logger.error(f"Bad option '{action}, must be 'create', 'show', 'hide', 'destroy'")


    def get_infos(self):
        """
        Get the infos entered by the user and return them
        """
        name = self.title_e.get()

        if name == "Tout les livres":
            self.error_b.grid(row=0, column=1, sticky="w")
            return 

        books = {}
        user_select = self.books_treeview.selection()

        for selection in user_select:
            selected_book_id = self.books_treeview.item(selection)["text"]
            selected_book = self.books_handler.get_book(internal_id=selected_book_id)
            books[selected_book_id]=selected_book[0]

        return {
            "shelf_name":name,
            "shelf_books":books,
            "shelf_id":str(dt.datetime.timestamp(dt.datetime.now())).replace(".", "")
        }
