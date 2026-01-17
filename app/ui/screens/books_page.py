
import logging
import customtkinter as ctk

from app.ui import my_frames
from app.ui.screens import book_creation_page
from app.src import book

class BooksTab(my_frames.MyFrame):

    def __init__(self, master, books_handler: book.BooksHandler, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler

    def draw_widgets(self):
        self.onread_books = OnReadBooks(self, self.books_handler, orientation="horizontal")
        self.onread_books.grid(row=0, column=0, sticky="nsew")
        self.onread_books.draw_widgets()
        self.add_b = ctk.CTkButton(self, text="add_circle", hover_color=self.onread_books.cget("bg_color"), fg_color=self.onread_books.cget("bg_color"), font=("Material Symbols Outlined 28pt", 40), command=self.add_book)
        self.add_b.grid(row=0, column=1)
        self.books_shelf = BooksShelf(self, self.books_handler)
        self.books_shelf.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.books_shelf.draw_widgets()
        self.book_creation_tp = ctk.CTkToplevel(self)
        self.book_creation_tp.title("New Book")
        self.book_creation_tp.protocol("WM_DELETE_WINDOW", self.on_closing_add_book_window)
        self.book_creation_tp.withdraw()
        self.book_creation_tp.columnconfigure(0, weight=1)
        self.book_creation_tp.rowconfigure(0, weight=1)
        self.book_creation_screen = book_creation_page.BooksCreationScreen(self.book_creation_tp, self.books_handler, self.books_shelf)
        self.book_creation_screen.grid(row=0, column=0, sticky="nsew")
        self.book_creation_screen.draw_widgets()

    def add_book(self):
        self.logger.info("Showing add books windows...")
        self.book_creation_tp.deiconify()

    def on_closing_add_book_window(self):
        self.logger.info("Hiding add books windows...")
        self.book_creation_tp.withdraw()

            
class BooksShelf(my_frames.MyScrollableFrame):

    def __init__(self, master, books_handler: book.BooksHandler, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=0)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.books_frames = {}

    def draw_widgets(self):
        self.update_books()

    def update_books(self):
        self.logger.info("Updating books frames...")
        index = 0

        for book_id, book in self.books_handler.books.items():
            book_fr = BookLocation(self, book)
            book_fr.draw_widgets()
            book_fr.grid(row=index, column=0)
            index += 1
            self.books_frames[book_id] = book_fr
            

class OnReadBooks(my_frames.MyScrollableFrame):

    def __init__(self, master, books_handler: book.BooksHandler, max=5, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler

    def draw_widgets(self):
        self.last_read_lb = ctk.CTkLabel(self, text="Lus récemments")
        self.last_read_lb.grid(row=0, column=0)

class BookLocation(my_frames.MyFrame):

    def __init__(self, master, book: book.Book):
        super().__init__(master)
        self.logger = logging.getLogger(__name__)
        self.book = book

    def draw_widgets(self):
        self.title_lb = ctk.CTkLabel(self, text=self.book.title, font=("default", 17), anchor="w")
        self.title_lb.grid(row=0, column=1, sticky="w")
        self.author_lb = ctk.CTkLabel(self, text=self.book.authors, anchor="w")
        self.author_lb.grid(row=1, column=1, sticky="w")
        self.edition_lb = ctk.CTkLabel(self, text=f"Edition : {self.book.edition if self.book.edition else "Unknown"}", anchor="w")
        self.edition_lb.grid(row=2, column=1, sticky="w")
        self.summary_tb = ctk.CTkTextbox(self)
        self.summary_tb.insert(0.0, text=self.book.summary)
        self.summary_tb.configure(state="disabled")
        self.summary_tb.grid(row=3, column=1, sticky="w")
