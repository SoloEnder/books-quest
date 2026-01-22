
import logging
import customtkinter as ctk

from app.ui import my_frames
from app.ui.screens import book_creation_page
from app.ui.screens import shelf_creation_page
from app.src import book

class BooksTab(my_frames.MyFrame):

    def __init__(self, master, books_handler: book.BooksHandler, events_handler, **kwargs):
        super().__init__(master, **kwargs)
        self.books_shelfs_fr = {}
        self.columnconfigure(0, weight=1)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.events_handler = events_handler


    def draw_widgets(self, event=None):
        self.columnconfigure(0, weight=1)
        self.add_book_b = ctk.CTkButton(self, text="add_circle", hover_color=self.cget("bg_color"), fg_color=self.cget("bg_color"), font=("Material Symbols Outlined 28pt", 40), command=lambda: self.switch_mode("book_creation"))
        self.add_book_b.grid(row=0, column=0, sticky="w")
        self.add_book_lb = ctk.CTkLabel(self, text="Ajouter un livre")
        self.add_book_lb.grid(row=0, column=0, sticky="e")
        self.add_shelf_lb = ctk.CTkLabel(self, text="Ajouter une étagère")
        self.add_shelf_lb.grid(row=1, column=0, sticky="e")
        self.add_shelf_b = ctk.CTkButton(self, text="add_circle", hover_color=self.cget("bg_color"), fg_color=self.cget("bg_color"), font=("Material Symbols Outlined 28pt", 40), command=lambda: self.switch_mode("shelf_creation"))
        self.add_shelf_b.grid(row=1, column=0, sticky="w")
        self.creation_tp = ctk.CTkToplevel(self)
        self.creation_tp.title("New Book") 
        self.creation_tp.protocol("WM_DELETE_WINDOW", self.on_closing_add_book_window)
        self.creation_tp.withdraw()
        self.creation_tp.columnconfigure(0, weight=1)
        self.creation_tp.rowconfigure(0, weight=1)
        self.book_creation_screen = book_creation_page.BooksCreationScreen(self.creation_tp, self.books_handler, self.events_handler)
        self.book_creation_screen.grid(row=0, column=0, sticky="nsew")
        self.book_creation_screen.draw_widgets()
        self.shelf_creation_screen = shelf_creation_page.ShelfCreationFrame(self.creation_tp, self.books_handler, self.events_handler)

        for index, books_shelf in enumerate(self.books_handler.books_shelfs.values()):
            self.rowconfigure(index+2, weight=1)
            book_shelf_fr = BooksShelfFrame(self, books_shelf, self.events_handler)
            book_shelf_fr.draw_widgets()
            book_shelf_fr.grid(row=index+2, column=0, sticky="nsew")

    def switch_mode(self, mode: str):
        """
        Switch the frame in the b
        """
        if mode == "shelf_creation":
            self.book_creation_screen.grid_remove()
            self.shelf_creation_screen.grid(row=0, column=0, sticky="nsew")
            self.shelf_creation_screen.draw_widgets()
            self.creation_tp.deiconify()

        elif mode == "book_creation":
            self.shelf_creation_screen.grid_remove()
            self.book_creation_screen.grid(row=0, column=0, sticky="nsew")
            self.book_creation_screen.draw_widgets()
            self.creation_tp.deiconify()

        else:
            raise ValueError(f"Unknown mode : {mode}")

    def add_book(self):
        self.logger.info("Showing add books windows...")
        self.book_creation_screen.draw_widgets()
        self.creation_tp.deiconify()

    def on_closing_add_book_window(self):
        self.logger.info("Hiding add books windows...")
        self.creation_tp.withdraw()
            
class BooksShelfFrame(my_frames.MyFrame):

    def __init__(self, master, books_self: book.BooksShelf, events_handler, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1)
        self.logger = logging.getLogger(__name__)
        self.books_shelf = books_self
        self.name = self.books_shelf.name
        self.events_handler = events_handler
        self.events_handler.add_listener("BookShelfUpdated", self.update_screen)
        self.books_frames = {}

    def update_screen(self, event):

        if event.kwargs.get("book_shelf_name") == self.name:
            self.draw_widgets()

    def draw_widgets(self):
        self.title_lb = ctk.CTkLabel(self, text=self.books_shelf.name, font=("default", 18, "bold"))
        self.title_lb.grid(row=0, column=0, sticky="sw")
        self.books_sf = ctk.CTkScrollableFrame(self, orientation="horizontal")
        self.books_sf.grid(row=1, column=0, sticky="nsew")
        self.logger.info("Drawing books frames...")
        index = 0

        for book_id, book in self.books_shelf.books.items():
            book_fr = BookLocation(self.books_sf, book, self.events_handler)
            book_fr.draw_widgets()
            book_fr.grid(row=0, column=index, padx=15)
            index += 1
            self.books_frames[book_id] = book_fr

class BookLocation(my_frames.MyFrame):

    def __init__(self, master, book: book.Book, events_handler):
        super().__init__(master)
        self.logger = logging.getLogger(__name__)
        self.book = book
        self.widgets = []
        self.events_handler = events_handler

    def draw_widgets(self):

        for widget in self.widgets:
            widget.destroy()

        self.authors_ft = ctk.CTkFont(slant="italic")
        self.title_lb = ctk.CTkLabel(self, text=f"{self.book.title}" if self.book.title else "Unknown ", font=("default", 17, "bold"))
        self.logger.debug(f"Book title label : {self.title_lb.cget("text")}")
        self.title_lb.grid(row=0, column=1, sticky="w")
        self.author_lb = ctk.CTkLabel(self, text=f"{self.book.authors} " if self.book.authors else "Unknown ", font=self.authors_ft)
        self.author_lb.grid(row=1, column=1, sticky="w")
        self.edition_lb = ctk.CTkLabel(self, text=f"Edition : {self.book.edition if self.book.edition else "Unknown"}")
        self.edition_lb.grid(row=2, column=1, sticky="w")
        self.read_pages_lb = ctk.CTkLabel(self, text=f"{self.book.alr_read_pages}/{self.book.tot_pages}")
        self.read_pages_lb.grid(row=3, sticky="w", column=1)
        self.read_pages_pb = ctk.CTkProgressBar(self, mode="determinate", height=12, width=120)
        self.read_pages_pb.set(self.book.alr_read_pages/self.book.tot_pages)
        self.read_pages_pb.grid(row=3, column=1, sticky="e")
        self.summary_tb = ctk.CTkTextbox(self)
        self.summary_tb.insert(0.0, text=self.book.summary)
        self.summary_tb.configure(state="disabled")
        self.summary_tb.grid(row=5, column=1, sticky="w")
        self.edit_b = ctk.CTkButton(self, text="edit", font=("Material Symbols Outlined 28pt", 22), width=4)
        self.edit_b.grid(row=6, column=1, sticky="w")
        self.delete_b = ctk.CTkButton(self, text="delete_forever", font=("Material Symbols Outlined 28pt", 22), fg_color=self.cget("bg_color"), width=4, text_color="red")
        self.delete_b.grid(row=6, column=1, sticky="e")
        self.widgets.extend(
            (
            self.title_lb,
            self.author_lb,
            self.edition_lb,
            self.read_pages_lb,
            self.summary_tb,
            self.edit_b,
            self.delete_b,
            )
        )

    def edit_me(self):
        self.events_handler.raise_event("BookEditionRequest")
