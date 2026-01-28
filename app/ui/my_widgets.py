
from tkinter.messagebox import showinfo, showerror, showwarning
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

class InfoButton(ctk.CTkButton):

    def __init__(self, master, window_text: str, window_title: str="Info", **kwargs):
        super().__init__(master, **kwargs)
        self.window_title = window_title
        self.window_text = window_text

    def draw_widgets(self):

        if not self.cget("text"):
            self.configure(text="info", font=("Material Symbols Outlined", 15), text_color="blue", fg_color=self.master.cget("fg_color"))

        self.configure(command=showinfo)

    def edit(self, window_title, window_text):
        self.window_title = window_title
        self.window_text = window_text

    def show_info(self):
        showinfo(title=self.window_title, message=self.window_text)

class ErrorButton(ctk.CTkButton):

    def __init__(self, master, window_title, window_text: str, **kwargs):
        super().__init__(master, **kwargs)
        self.window_title = window_title
        self.window_text = window_text

    def draw_widgets(self):

        if not self.cget("text"):
            self.configure(text="error", font=("Material Symbols Outlined", 13), text_color="red", fg_color=self.master.cget("fg_color"))

        self.configure(command=self.show_error)

    def edit(self, window_title, window_text):
        self.window_title = window_title
        self.window_text = window_text

    def show_error(self):
        showerror(title=self.window_title, message=self.window_text)

class WarningButton(ctk.CTkButton):

    def __init__(self, master, window_title, window_text: str, **kwargs):
        super().__init__(master, **kwargs)
        self.window_title = window_title
        self.window_text = window_text

    def draw_widgets(self):

        if not self.cget("text"):
            self.configure(text="warning", font=("Material Symbols Outlined", 13), text_color="yellow", fg_color=self.master.cget("fg_color"))

        self.configure(command=self.show_warning)

    def edit(self, window_title, window_text):
        self.window_title = window_title
        self.window_text = window_text

    def show_warning(self):
        showerror(title=self.window_title, message=self.window_text)
