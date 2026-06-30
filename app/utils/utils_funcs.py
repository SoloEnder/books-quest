import datetime as dt
import logging

from PySide6 import QtWidgets

from app.src import book_sys


def unknown_book_title_fmt(book: book_sys.Book):
    creation_date = dt.datetime.fromtimestamp(float(book.id))
    return f"[Untitled]-{creation_date.date()}"


def unknown_shelf_name_fmt(shelf: book_sys.Shelf):
    creation_date = dt.datetime.fromtimestamp(float(shelf.id))
    return f"[Unnamed]-{creation_date.date()}"


def add_title_suffix(
    title: str,
    title_suffix,
) -> str:
    """
    Add the suffix of a book/shelf title and return the result

    Parameters
    ----------
    title (str): the title
    title_suffix (str): the title suffix

    Returns
    -------
    str: the result text
    """
    return f"{title} ({title_suffix})" if title_suffix else title


def load_and_set_ss(
    *filepaths, widget: QtWidgets.QWidget, logger: logging.Logger | None = None
):
    combined_ss = ""

    for filepath in filepaths:
        try:
            with open(filepath, "r") as f:
                ss = f.read()

        except:
            if logger:
                logger.exception(
                    f"Couldn't load style file at {filepath}, skipping it (see logs for more infos)"
                )

        else:
            combined_ss += f"\n{ss}"

    widget.setStyleSheet(combined_ss)
