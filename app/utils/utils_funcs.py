
import datetime as dt
from app.src import book_sys
from PySide6 import QtWidgets
import logging

def unknown_book_title_fmt(book: book_sys.Book):
    creation_date = dt.datetime.fromtimestamp(float(book.internal_id))
    return f"[Untitled]-{creation_date.date()}"

def unknown_shelf_name_fmt(shelf: book_sys.Shelf):
    creation_date = dt.datetime.fromtimestamp(float(shelf.id))
    return f"[Unnamed]-{creation_date.date()}"

def set_displayed_names(names: list|tuple) -> list:
    """
    Check the number of occurrences of the same string in <names> and format it accordingly.
    Example:
        names = ["one", "two", "one", "three", "three", "three"]

        then the result will be:
        ["one", "two", "one (1)", "three", "three (1)", "three (2)"]
    """
    displayed_names = []
    checked_names = []

    for name in names:
        tmp_count = 0
        final_name = name
        if name in checked_names:
            for checked_name in checked_names:
                if name == checked_name:
                    tmp_count+=1

            if tmp_count:
                final_name = f"{name} ({tmp_count})"
        checked_names.append(name)
        displayed_names.append(final_name)

    return displayed_names

def load_and_set_ss(filepath: str, widget: QtWidgets.QWidget, logger: logging.Logger|None=None):
    try: 
        with open(filepath, "r") as f:
            ss = f.read()

        widget.setStyleSheet(ss)

    except:

        if logger:
            logger.exception(f"Couldn't set stylesheet for widget {widget}")