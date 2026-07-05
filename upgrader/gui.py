import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("450x300")
        self.installation_selection_sc = InstallationSelectionScreen(self)
        self.update_progress_sc = UpdateProgressScreen(self)
        self.update_error_sc = UpdateErrorScreen(self)
        self.update_success_sc = UpdateSuccessScreen(self)
        self.screens = {
            "installation_selection_screen": self.installation_selection_sc,
            "update_progress_screen": self.update_progress_sc,
            "update_error_screen": self.update_error_sc,
            "update_success_screen": self.update_success_sc,
        }
        self.current_screen_infos: tuple[str, tk.Frame] = (
            "installation_selection_screen",
            self.screens["installation_selection_screen"],
        )
        self.upgrader_version = ""
        self.about_b = ttk.Button(self, text="About", command=self.about)
        self.about_b.pack(pady=20)
        self.switch_screen(self.current_screen_infos[0])

    def about(self):
        tkinter.messagebox.showinfo(
            title="About",
            message=f"Books Quest Upgrader version {self.upgrader_version}",
        )

    def switch_screen(self, screen_name: str) -> tk.Frame:
        """
        Switch the currently displayed screen to `screen_name` and return the screen object
        """
        for screen in self.screens.values():
            screen.pack_forget()
        self.about_b.pack_forget()
        selected_screen = self.screens[screen_name]
        selected_screen.pack()
        self.about_b.pack()
        self.current_screen_infos = (screen_name, selected_screen)
        self.update()
        self.update_idletasks()
        return selected_screen

    def get_installation_folder(self) -> str:
        return self.installation_selection_sc.installation_path_sv.get()


class InstallationSelectionScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.installation_path_lb = ttk.Label(
            self,
            text="Please enter the path to the BooksQuest instance to be updated.",
        )
        self.installation_path_lb.grid(row=0, column=0, columnspan=2)
        self.warning_lb = ttk.Label(
            self,
            text="!!! Please ensure that the instance is not active, and make sure to remove quotation marks around the path !!!",
        )
        self.warning_lb.grid(row=1, column=0, columnspan=2)
        self.installation_path_sv = tk.StringVar(self)
        self.select_path_b = ttk.Button(
            self, text="Select...", command=self.select_folder
        )
        self.select_path_b.grid(row=2, column=0)
        self.installation_path_e = ttk.Entry(
            self, textvariable=self.installation_path_sv
        )
        self.installation_path_e.grid(row=2, column=1)
        self.confirm_b = ttk.Button(self, text="Start update")
        self.confirm_b.grid(row=3, column=0, columnspan=2)

    def select_folder(self):
        self.installation_path_sv.set(tkinter.filedialog.askdirectory())


class UpdateProgressScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.update_in_progress_lb = ttk.Label(
            self,
            text="Update in progress, do not close the program or launch the update installation...",
        )
        self.update_in_progress_lb.pack()
        self.operations_count = 1
        self.update_in_progress_pb = ttk.Progressbar(
            self, mode="determinate", orient="horizontal", length=300
        )
        self.update_in_progress_pb.pack()

    def set_operations_count(self, count: int):
        self.operations_count = count if count != 0 else 1

    def progress(self, step):
        value = (step / self.operations_count) * 100
        self.update_in_progress_pb["value"] += value
        self.update()


class UpdateErrorScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.error = ""
        self.error_lb = ttk.Label(
            self,
            text="Sorry, an error occurred and the update could not be completed successfully !",
        )
        self.error_lb.pack()
        self.cancel_b = ttk.Button(self, text="Cancel and quit")
        self.cancel_b.pack()
        self.show_error_b = ttk.Button(self, text="Show error", command=self.show_error)
        self.show_error_b.pack()
        self.copy_error_b = ttk.Button(self, text="Copy error", command=self.copy_error)
        self.copy_error_b.pack()

    def show_error(self):
        tkinter.messagebox.showerror("Upgrader error", message=self.error)

    def copy_error(self):
        self.clipboard_clear()
        self.clipboard_append(self.error)
        self.update()
        tkinter.messagebox.showinfo(
            title="BooksQuest Upgrader", message="Error copied to clipboard"
        )


class UpdateFinishProgress(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.cancel_progress_lb = ttk.Label(
            self,
            text="Finishing update, do not close the window or launch the installation",
        )
        self.cancel_progress_lb.pack()


class UpdateSuccessScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.success_lb = tk.Label(
            self,
            text="Your BooksQuest instance has been successfully updated\nYou can close this window",
        )
        self.success_lb.pack()
