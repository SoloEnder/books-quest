import os
import subprocess
import tkinter.messagebox
import traceback

import applier
import gui
import utils

UPGRADER_VERSION = "1.0.0"

w = gui.Window()
w.switch_screen("installation_selection_screen")
w.upgrader_version = UPGRADER_VERSION


def no_exit():
    pass


class InvalidInstallationError(utils.MyBaseException):
    def __init__(self, given_path: str):
        super().__init__()
        self.given_path = given_path
        self.msg = f"Element at {self.given_path} is not recognized as a valid BooksQuest installation !"


def check_installation(installation_path: str):
    if not os.path.isdir(installation_path):
        NotADirectoryError(f"Element at {installation_path} is not a directory !")

    app_folder = os.path.join(installation_path, "app")
    app_infos = os.path.join(app_folder, "app_infos.json")
    updater_file = os.path.join(installation_path, "updater.exe")
    main_file = os.path.join(installation_path, "books-quest.exe")
    excepted_content = (app_folder, app_infos, updater_file, updater_file, main_file)

    for excepted in excepted_content:
        if not os.path.exists(excepted):
            raise InvalidInstallationError(installation_path)


def finish_update(
    updater_path,
    installation_path: str,
):
    w.protocol("WM_DELETE_WINDOW", no_exit)
    w.switch_screen("update_finish_progress_screen")
    p = subprocess.run(
        [
            updater_path,
            installation_path,
            "-c",
        ],
        capture_output=True,
    )
    if p.returncode != 0:
        tkinter.messagebox.showerror(
            title="Upgrader error",
            message=f"Unable to finish properly update due to the following error : \n{p.stderr or p.stdout}",
        )
    w.destroy()
    input("Type Something to exit")


def try_update():
    installation_path = w.get_installation_folder()

    try:
        check_installation(installation_path)

    except (NotADirectoryError, InvalidInstallationError):
        tkinter.messagebox.showerror(message="Invalid installation folder !")

    else:
        updater_path = os.path.join(installation_path, "updater.exe")
        try:
            w.switch_screen("update_progress_screen")
            w.protocol("WM_DELETE_WINDOW", func=no_exit)
            applier.run(installation_path)

        except Exception:
            w.protocol(
                "WM_DELETE_WINDOW",
                lambda: finish_update(updater_path, installation_path),
            )
            w.update_error_sc.cancel_b.config(
                command=lambda: finish_update(updater_path, installation_path)
            )
            w.update_error_sc.error_t.insert(
                0.0,
                f"Couldn't perform update due to the follwing error :\n{traceback.format_exc()}",
            )
            w.switch_screen("update_error_screen")

        else:
            w.protocol(
                "WM_DELETE_WINDOW",
                lambda: finish_update(updater_path, installation_path),
            )
            w.switch_screen("update_success_screen")


w.installation_selection_sc.confirm_b.config(command=try_update)
w.mainloop()
