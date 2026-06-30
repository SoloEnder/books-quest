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


def format_displayed_title(
    title: str,
    format: str = "<title> (<title_suffix>)",
    **kwargs,
) -> str:
    """
    Format the displayed title by replacing the placeholders in `format` by their value given in `kwargs`
    In `format`, each argument must be placed between '<>'.

    Parameters
    ----------
    title (str): the title to format
    format (str): the excepted output (where each arg will be replaced by its value)

    Returns
    -------
    str: the formatted text

    Example
    -------
    `format_dispkayer_title(title="Book", format="<title> (<occurence_count>)", occurence_count=10)`
    will return : "Book (10)"
    """
    formatted_title = format
    formatted_title.replace(f"<{title}>", title)
    for key, value in kwargs.items():
        if not value:
            value = ""
        formatted_title.replace(f"<{key}>", value)
    return formatted_title


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
