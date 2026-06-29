import os
import subprocess
import sys
import tkinter.messagebox
import traceback

import applier
import gui
import utils

# parser = argparse.ArgumentParser()
# parser.add_argument(
#     "installation_path",
#     help="The path to the folder where is located the installation to update",
# )
# parser.add_argument(
#     "--no_gui",
#     action="store_true",
#     help="The path to the folder where is located the installation to update",
# )
# args = parser.parse_args()
# installation_path = args.installation_path
w = gui.Window()
w.installation_selection()
w.resizable(False, False)


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
    main_file = os.path.join(installation_path, "books_quest.exe")
    excepted_content = (app_folder, app_infos, updater_file, updater_file, main_file)

    for excepted in excepted_content:
        if not os.path.exists(excepted):
            raise InvalidInstallationError(installation_path)


def finish_update(updater_path, installation_path: str):
    print(updater_path, installation_path)

    try:
        subprocess.run(
            [
                updater_path,
                installation_path,
                "-c",
            ]
        )

    except Exception:
        tkinter.messagebox.showerror(
            "Failed to cancel update, your installation may be corrupted"
        )
    w.destroy()
    sys.exit()


def try_update():
    installation_path = w.installation_selection_fr.installation_path_sv.get()

    try:
        check_installation(installation_path)

    except (NotADirectoryError, InvalidInstallationError):
        tkinter.messagebox.showerror(message="Invalid installation folder !")

    else:
        updater_path = os.path.join(installation_path, "updater.exe")
        w.update_screen()
        w.protocol("WM_DELETE_WINDOW", func=no_exit)
        try:
            applier.run(installation_path)

        except Exception:
            w.protocol(
                "WM_DELETE_WINDOW",
                lambda: finish_update(updater_path, installation_path),
            )
            w.error_screen_fr.cancel_b.config(
                command=lambda: finish_update(updater_path, installation_path)
            )
            w.error_screen_fr.cancel_msg_sv.set(
                f"Couldn't perform update due to the follwing error :\n{traceback.format_exc()}"
            )
            w.error_screen()

        else:
            print(updater_path)
            w.protocol(
                "WM_DELETE_WINDOW",
                lambda: finish_update(updater_path, installation_path),
            )
            w.sucess_screen()


w.installation_selection_fr.confirm_b.config(command=try_update)
w.mainloop()
