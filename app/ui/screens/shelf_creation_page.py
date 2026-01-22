
from tkinter import ttk
import customtkinter as ctk

from app.ui import my_frames

class ShelfCreationFrame(my_frames.MyScrollableFrame):

    def __init__(self, master, books_handler, events_handler, **kwargs):
        super().__init__(master, **kwargs)
        self.books_handler = books_handler
        self.events_handler = events_handler

    def draw_widgets(self):
        self.title_lb = ctk.CTkLabel(self, text="Titre")
        self.title_lb.grid(row=0, column=0, sticky="w")
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
        self.validate_b = ctk.CTkButton(self, text="Ajouter")
        self.validate_b.grid(row=0, column=1, rowspan=2)

    def create_book_shelf(self):
        book_shelf_infos = self.get_infos()

    def get_infos(self):
        """
        Get the infos entered by the user and return them
        """
        title = self.title_e.get()
        content = []

        user_select = self.books_treeview.selection()

        for selection in user_select:
            selected_book_id = self.books_treeview.item(selection)["text"]
            selected_book = self.books_handler.books[selected_book_id]
            content.append(selected_book)

        return {
            "title":title,
            "content":content
        }



