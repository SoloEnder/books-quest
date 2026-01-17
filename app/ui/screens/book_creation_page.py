
import customtkinter as ctk

from app.ui import my_frames
from app.src import book

class BooksCreationScreen(my_frames.MyScrollableFrame):

    def __init__(self, master, books_handler: book.BooksHandler, books_frames_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.books_handler = books_handler
        self.books_frames_manager = books_frames_manager

    def draw_widgets(self):
        self.title_lb = ctk.CTkLabel(self, text="Titre (obligatoire)")
        self.title_lb.grid(row=0, column=0, sticky="w")
        self.title_e = ctk.CTkEntry(self, width=250)
        self.title_e.grid(row=1, column=0, sticky="w")
        self.authors_lb = ctk.CTkLabel(self, text="Autheur")
        self.authors_lb.grid(row=2, column=0, sticky="w")
        self.authors_e = ctk.CTkEntry(self)
        self.authors_e.grid(row=3, column=0, sticky="w")
        self.edition_lb = ctk.CTkLabel(self, text="Edition")
        self.edition_lb.grid(row=4, column=0, sticky="w")
        self.edition_e = ctk.CTkEntry(self)
        self.edition_e.grid(row=5, column=0, sticky="w")
        self.isbn_lb = ctk.CTkLabel(self, text="ISBN")
        self.isbn_lb.grid(row=6, column=0, sticky="w")
        self.isbn_e = ctk.CTkEntry(self)
        self.isbn_e.grid(row=7, column=0, sticky="w")
        self.summary_lb = ctk.CTkLabel(self, text="Resumé")
        self.summary_lb.grid(row=8, column=0, sticky="w")
        self.summary_tb = ctk.CTkTextbox(self)
        self.summary_tb.grid(row=9, column=0, sticky="we")
        self.add_b = ctk.CTkButton(self, text="Ajouter", command=self.add_book)
        self.add_b.grid(row=10, sticky="w")

    def add_book(self):
        """
        Get information entered by the user about a book, create it and add it to the book database
        """

        title = self.title_e.get()
        authors = self.authors_e.get()
        isbn = self.isbn_e.get()
        editions = self.edition_e.get()
        summary = self.summary_tb.get(0.0, ctk.END)
        self.books_handler.add_books(title=title, isbn=isbn, authors=authors, editions=editions, summary=summary)

        if self.books_frames_manager:
            self.books_frames_manager.update_books()

    
