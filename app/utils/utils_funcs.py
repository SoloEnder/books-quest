import datetime as dt
import logging

from PySide6 import QtWidgets

from app.src import book_sys, langs_handler


def get_reading_state_tr(
    reading_state: book_sys.Book.ReadingState, langs_handler: langs_handler.LangsHandler
) -> str:
    """
    Return the translation of a book reading state

    Parameters
    ----------
    - reading_state: the reading state of the book
    - langs_handler: an `LangsHandler` instance

    Returns
    -------
    - str: the translation
    """
    reading_state_tr = {
        "UNREAD": langs_handler.tr("book.infos.reading_state.unread"),
        "CURRENTLY_READING": langs_handler.tr(
            "book.infos.reading_state.currently_reading"
        ),
        "FINISHED": langs_handler.tr("book.infos.reading_state.finished"),
    }
    return reading_state_tr[reading_state.value]


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


def get_title_suffix(
    obj_with_the_same_title: book_sys.ShelvesList | book_sys.BooksList,
) -> int | None:
    """
    Select an appropriate title suffix (the number following the shelf/book title) for the shelf/book being created;
    the suffix is initially set based on the number of shelves/books with the same title,
    and is then determined by adding 1 to the highest title suffix found among shelves/books sharing the same title as the one being created.

    Parameters
    ----------
    obj_with_the_same_title (ShelvesList): a list of shelves that share the same title as the one being created

    Returns
    -------
    int: the title suffix found
    """
    title_suffix = len(obj_with_the_same_title)

    for obj in obj_with_the_same_title:
        if obj.title_suffix:
            if obj.title_suffix >= title_suffix:
                title_suffix = obj.title_suffix + 1

    return title_suffix


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
