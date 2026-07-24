import logging
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk

logger = logging.getLogger("updater.gui")


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Updater")
        self.geometry("450x300")
        self.installation_selection_sc = InstallationSelectionScreen(self)
        self.work_in_progress_sc = WorkInProgressScreen(self)
        self.update_error_sc = UpdateErrorScreen(self)
        self.update_success_sc = UpdateSuccessScreen(self)
        self.screens = {
            "installation_selection_screen": self.installation_selection_sc,
            "work_in_progress_screen": self.work_in_progress_sc,
            "update_error_screen": self.update_error_sc,
            "update_success_screen": self.update_success_sc,
        }
        self.current_screen_infos: tuple[str, tk.Frame] = (
            "installation_selection_screen",
            self.screens["installation_selection_screen"],
        )
        self.updater_version = ""
        self.about_b = ttk.Button(self, text="About", command=self.about)
        self.about_b.pack(pady=20)
        self.switch_screen(self.current_screen_infos[0])

    def about(self):
        tkinter.messagebox.showinfo(
            title="About",
            message=f"Books Quest Updater version {self.updater_version}",
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
            text="!!! 1) Please ensure that the instance is not active. \n2) and make sure to remove quotation marks around the path !!!",
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


class WorkInProgressScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.operations_groups = {
            "default": {
                "name": "default",
                "msg": "Work in progress, please wait...",
                "operations_count": 1,
                "progress": 0,
            }
        }
        self.work_in_progress_lb = ttk.Label(
            self,
            text="Work in progress, do not close the program or launch the installation...",
        )
        self.current_operations_group = self.operations_groups["default"]
        self.work_in_progress_lb.pack()
        self.current_operations_group_msg_lb = tk.Label(
            self, text=self.current_operations_group["msg"], anchor="w"
        )
        self.current_operations_group_msg_lb.pack(pady=5)
        self.work_in_progress_pb = ttk.Progressbar(
            self, mode="determinate", orient="horizontal", length=300
        )
        self.work_in_progress_pb.pack()

    def progress_group(self, group_name: str | None = None, step: int = 1):
        if group_name:
            group = self.operations_groups[group_name]

        else:
            group = self.current_operations_group

        if group["operations_count"] < 1:
            logger.error(
                f"Aborting operations progress for operations group '{group_name}', because operations count is under 0 !"
            )
            return
        group["progress"] += step
        self.work_in_progress_pb["value"] = (
            group["progress"] / group["operations_count"] * 100
        )
        self.update()

    def add_operations_group(
        self,
        group_name: str,
        group_msg: str,
        operations_count: int = 1,
        progress: int = 0,
        set_as_current: bool = True,
    ):
        """
        Adds an new group of operations.

        Parameters
        ----------
        group_name (str): the name of the group (e.g. "files_removing")
        group_msg (str): the message displayed to the user for this group (e.g. "Removing files...")
        operations_count (int): the count of operation that this group do
        progress (int=0): the progress of the operations, used to update the progress bar
        set_default (bool=True): wether to set the created operations group as the current operations group
        """
        logger.info(f"Adding new operations group '{group_name}'")
        self.operations_groups[group_name] = {
            "name": group_name,
            "msg": group_msg,
            "operations_count": operations_count,
            "progress": progress,
        }

        if set_as_current:
            self.set_current_operations_group(group_name)
            return
        self._update_current_operation_group()

    def set_current_operations_group(self, group_name: str):
        """
        Set the current operation group

        Parameters
        ----------
        - group_name (str): the group name to set.
        """
        logger.info(f"Setting current operations group as '{group_name}'")
        self.current_operations_group = self.operations_groups[group_name]
        self._update_current_operation_group()

    def _update_current_operation_group(self):
        self.current_operations_group_msg_lb.config(
            text=self.current_operations_group["msg"]
        )
        self.progress_group(step=0)

    def edit_operations_group(self, group_name: str | None = None, **kwargs):
        """
        Edits the data of an operation group

        Parameters
        ----------
        - group_name (str|None=None): the name of the group to edit. If equal to None, then the current operations group is used.
        - **kwargs: the key of the entries to edit, and their new values
        """

        if group_name:
            group = self.operations_groups[group_name]

        else:
            group = self.current_operations_group

        for key, value in kwargs:
            group[key] = value

        self._update_current_operation_group()


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


class UpdateSuccessScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.success_lb = tk.Label(
            self,
            text="Your BooksQuest instance has been successfully updated\nYou can close this window",
        )
        self.success_lb.pack()
