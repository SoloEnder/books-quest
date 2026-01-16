
import logging

from app.ui import ui
from app.src import book

class App:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialising application...")
        self.books_handler = book.BooksHandler()
        self.ui = ui.UI(self, self.books_handler)

        
    def running(self):
        self.logger.info("Showing main window...")
        self.ui.mainloop()
