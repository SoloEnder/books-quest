
import datetime as dt
from app.src import book_sys

def unknown_book_title_fmt(book: book_sys.Book):
    return f"[Untitled]-{dt.datetime.fromtimestamp(float(book.internal_id))}"

def unknown_shelf_name_fmt(shelf: book_sys.Shelf):
    creation_date = dt.datetime.fromtimestamp(float(shelf.id))
    return f"[Unnamed]-{creation_date.date()}"