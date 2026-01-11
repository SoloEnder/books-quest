
from app.ui import ui

class App:

    def __init__(self):
        self.ui = ui.UI(self)
        
    def running(self):
        self.ui.mainloop()
