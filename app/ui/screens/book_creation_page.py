
import typing
import logging
import datetime as dt
import customtkinter as ctk
from tkinter.messagebox import showerror

from app.ui import my_frames
from app.src import book

class BooksCreationScreen(my_frames.MyScrollableFrame):

    def __init__(self, master, books_handler: book.BooksHandler, events_handler, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.books_handler = books_handler
        self.events_handler = events_handler
        self.events_handler.create_event("BookLocationCreationRequest", book_object=None)

    def draw_widgets(self):
        self.error_b = ctk.CTkButton(self, text="error", font=("Material Symbols Outlined 28pt", 13), width=4, fg_color=self.cget("bg_color"), text_color="red")
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
        self.tot_pages_lb = ctk.CTkLabel(self, text="Nombre de pages")
        self.tot_pages_lb.grid(row=10, sticky="w")
        self.tot_pages_iv = ctk.IntVar()
        self.tot_pages_e = ctk.CTkEntry(self)
        self.tot_pages_e.bind("<KeyRelease>", self.get_tot_pages)
        self.tot_pages_e.insert(0, 1)
        self.tot_pages_e.grid(row=11, sticky="w")
        self.tot_pages_iv = ctk.IntVar(self)
        self.alr_read_pages_lb = ctk.CTkLabel(self, text="Nombre de pages lues")
        self.alr_read_pages_lb.grid(row=12, sticky="w")
        self.alr_read_pages_select_mode = ctk.CTkTabview(self, anchor="w", height=50)
        self.alr_read_pages_select_mode.add("Slider")
        self.alr_read_pages_select_mode.add("Champs")
        self.alr_read_pages_sl = ctk.CTkSlider(self.alr_read_pages_select_mode.tab("Slider"), from_=0, to=1, variable=self.tot_pages_iv, width=320)
        self.alr_read_pages_sl.set(0)
        self.alr_read_pages_sl.grid(row=0, column=0, sticky="w")
        self.alr_read_pages_lb = ctk.CTkLabel(self.alr_read_pages_select_mode.tab("Slider"), textvariable=self.tot_pages_iv)
        self.alr_read_pages_lb.grid(row=14, sticky="w")
        self.alr_read_pages_e = ctk.CTkEntry(self.alr_read_pages_select_mode.tab("Champs"))
        self.alr_read_pages_e.grid(row=0, column=0, sticky="w")
        self.alr_read_pages_select_mode.grid(row=13, column=0, sticky="w")
        self.book_shelf_lb = ctk.CTkLabel(self, text="Etagères")
        self.book_shelf_lb.grid(row=15, sticky="w")
        self.book_shelf_cbs = {}
        
        for index, book_shelf in enumerate(self.books_handler.books_shelfs.values()):

            book_shelf_cb = ctk.CTkCheckBox(self, text=book_shelf.name)
            book_shelf_cb.grid(row=index+16, sticky="w")

            if book_shelf.name == "Tout les livres":
                book_shelf_cb.configure(state="disabled")
                book_shelf_cb.select()

            self.book_shelf_cbs[book_shelf.name] = book_shelf_cb

        self.add_b = ctk.CTkButton(self, text="Ajouter", command=self.add_book)
        self.add_b.grid(row=len(self.book_shelf_cbs)+16, sticky="w")

    def get_tot_pages(self, event):
        tot_pages = self.tot_pages_e.get()

        if tot_pages.isdigit():
            tot_pages = int(tot_pages)

            if tot_pages <= 0:
                tot_pages = 1

        else:
            tot_pages = 1

        self.alr_read_pages_sl.configure(to=tot_pages)
        self.alr_read_pages_sl.set(0)


    def add_book(self):
        """
        Get information entered by the user about a book, create it and add it to the book database
        """

        books_infos = self.get_book_infos()

        if books_infos:
            self.events_handler.raise_event("BookCreationRequest", **books_infos)

    def get_book_infos(self):
        all_right = False

        if self.alr_read_pages_select_mode.get() == "Slider":
            alr_read_pages = int(self.alr_read_pages_sl.get())
            all_right = True

        elif self.alr_read_pages_select_mode.get() == "Champs":

            if self.alr_read_pages_e.get().isdigit():
                self.error_b.grid_remove()
                alr_read_pages = int(self.alr_read_pages_e.get())
                all_right = True

            else:
                self.error_b.configure(command=lambda: showerror(title="!", message="Veuillez entrer un nombre entier !"))
                self.error_b.grid(row=12, sticky="e")

        title = self.title_e.get()
        authors = self.authors_e.get()
        isbn = self.isbn_e.get()
        edition = self.edition_e.get()
        summary = self.summary_tb.get(0.0, ctk.END)
        tot_pages = self.alr_read_pages_sl.cget("to")
        books_shelfs = []

        for shelf_name, shelf_cbs in self.book_shelf_cbs.items():

            if shelf_cbs.get() == 1:
                books_shelfs.append(shelf_name)

        if all_right == True:
            return {
                "title":title, 
                "authors":authors, 
                "isbn":isbn, 
                "edition":edition, 
                "summary":summary, 
                "tot_pages":tot_pages,
                "alr_read_pages":alr_read_pages,
                "books_shelfs":books_shelfs,
                "internal_id":str(dt.datetime.timestamp(dt.datetime.now())).replace(".", "")
                }

    def editions_mode(self, book: book.Book):
        self.title_e.delete(0, ctk.END)
        self.title_e.insert(0, book.title)
        self.authors_e.delete(0, ctk.END)
        self.authors_e.insert(0, book.authors)
        self.isbn_e.delete(0, ctk.END)
        self.isbn_e.insert(0, book.isbn)
        self.summary_tb.delete(0.0, ctk.END)
        self.summary_tb.insert(0.0, ctk.END)
        self.tot_pages_e.delete(0, ctk.END)
        self.tot_pages_e.insert(0, book.tot_pages)
        self.get_tot_pages()
        self.alr_read_pages_sl.set(book.alr_read_pages)
        self.add_b.configure(text="Edit")
