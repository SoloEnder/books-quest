
import logging

from app.ui import ui

class App:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialising application...")
        self.ui = ui.UI(self)

        
    def running(self):
        self.logger.info("Showing main window...")
        self.ui.mainloop()
