import tkinter as tk
import tkinter.filedialog
from tkinter import ttk


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.installation_selection_fr = SelectInstallationFolderFrame(self)
        self.update_in_progress_fr = UpdateScreen(self)
        self.cancel_screen_fr = CancelScreen(self)
        self.sucess_screen_fr = SuccessScreen(self)

    def update_screen(self):
        self.sucess_screen_fr.pack_forget()
        self.installation_selection_fr.pack_forget()
        self.cancel_screen_fr.pack_forget()
        self.update_in_progress_fr.pack()

    def cancel_screen(self):
        self.installation_selection_fr.pack_forget()
        self.update_in_progress_fr.pack_forget()
        self.cancel_screen_fr.pack()

    def installation_selection(self):
        self.sucess_screen_fr.pack_forget()
        self.update_in_progress_fr.pack_forget()
        self.cancel_screen_fr.pack_forget()
        self.installation_selection_fr.pack()

    def sucess_screen(self):
        self.update_in_progress_fr.pack_forget()
        self.cancel_screen_fr.pack_forget()
        self.installation_selection_fr.pack_forget()
        self.sucess_screen_fr.pack()


class SelectInstallationFolderFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.installation_path_lb = tk.Label(
            self,
            text="Please enter the path to the BooksQuest instance to be updated.",
        )
        self.installation_path_lb.grid(row=0, column=0, columnspan=2)
        self.warning_lb = tk.Label(
            self, text="!!! Please ensure that the instance is not active !!!"
        )
        self.warning_lb.grid(row=1, column=0, columnspan=2)
        self.installation_path_sv = tk.StringVar(self)
        self.select_path_b = tk.Button(
            self, text="Select...", command=self.select_folder
        )
        self.select_path_b.grid(row=2, column=0)
        self.installation_path_e = tk.Entry(
            self, textvariable=self.installation_path_sv
        )
        self.installation_path_e.grid(row=2, column=1)
        self.confirm_b = tk.Button(self, text="Start update")
        self.confirm_b.grid(row=3, column=0, columnspan=2)

    def select_folder(self):
        self.installation_path_sv.set(tkinter.filedialog.askdirectory())


class UpdateScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.update_in_progress_lb = tk.Label(self, text="Update in progress...")
        self.update_in_progress_lb.pack()
        self.update_progress_pb = ttk.Progressbar(self, mode="indeterminate")
        self.update_progress_pb.pack()
        self.update_progress_pb.start()


class CancelScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.cancel_msg_sv = tk.StringVar()
        self.canceled_lb = tk.Label(self, textvariable=self.cancel_msg_sv)
        self.canceled_lb.pack()
        self.cancel_b = tk.Button(self, text="Cancel")
        self.cancel_b.pack()


class SuccessScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.success_lb = tk.Label(
            self,
            text="Your BooksQuest instance has been successfully updated, you can close this window",
        )
        self.success_lb.pack()
