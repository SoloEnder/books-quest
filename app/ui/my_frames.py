
import customtkinter as ctk

class MyFrame(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def draw_widgets(self):
        pass

class MyScrollableFrame(ctk.CTkScrollableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def draw_widgets(self):
        pass