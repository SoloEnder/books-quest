import datetime as dt
import logging

from PySide6 import QtWidgets

from app.src import book_sys
from app.src.services import langs


def get_reading_state_tr(
    reading_state: book_sys.Book.ReadingState, langs: langs.LangsService
) -> str:
    """
    Return the translation of a book reading state

    Parameters
    ----------
    - reading_state: the reading state of the book
    - langs: an `LangsService` instance

    Returns
    -------
    - str: the translation
    """
    reading_state_tr = {
        "UNREAD": langs.tr("book.infos.reading_state.unread"),
        "CURRENTLY_READING": langs.tr("book.infos.reading_state.currently_reading"),
        "FINISHED": langs.tr("book.infos.reading_state.finished"),
    }
    return reading_state_tr[reading_state.value]


def unknown_book_title_fmt(book: book_sys.Book):
    creation_date = dt.datetime.fromtimestamp(float(book.id))
    return f"[Untitled]-{creation_date.date()}"


def unknown_shelf_name_fmt(shelf: book_sys.Shelf):
    creation_date = dt.datetime.fromtimestamp(float(shelf.id))
    return f"[Unnamed]-{creation_date.date()}"


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
