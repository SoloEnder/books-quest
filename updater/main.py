import argparse
import datetime as dt
import logging
import logging.handlers
import os
import pathlib
import sys
import tkinter.messagebox
import traceback

import applier
import clean
import gui
import migrate
import undo
import utils

VERSION = "2.0.0"
logger = logging.getLogger("updater")
logger.propagate = False
rt_files_handler = logging.handlers.RotatingFileHandler("updater.log")
rt_files_handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
logs_fmt = logging.Formatter(
    fmt="[{asctime}] - [{name}/{levelname}] : {message}", style="{"
)
stream_handler.setFormatter(logs_fmt)
stream_handler.setLevel(logging.DEBUG)
rt_files_handler.setFormatter(logs_fmt)
logger.addHandler(stream_handler)
logger.addHandler(rt_files_handler)
logger.setLevel(logging.DEBUG)


def no_exit():
    pass


def check_installation(installation_path: str, update_infos: dict) -> dict | None:
    logger.info("Checking installation folder...")

    if not os.path.exists(installation_path):
        logger.error(f"Path '{installation_path}' does not exists, aborting update.")
        tkinter.messagebox.showerror(
            title="Updater", message="This path does not exists !"
        )
        return

    installation_app_infos = utils.get_installation_app_infos(installation_path)

    some_compatibility(installation_app_infos)

    if utils.ishigher(installation_app_infos["app_version"], update_infos["update_to"]):
        logger.error(
            f"Installation version ({installation_app_infos['app_version']}) is higher than update version {update_infos['update_to']}, aborting update."
        )
        tkinter.messagebox.showerror(
            f"The installation version ({installation_app_infos['app_version']}) is already higher than this update ({update_infos['update_to']})"
        )
        return

    return installation_app_infos


def check_update() -> dict | None:
    logger.info("Checking update...")
    update_infos = utils.get_manifest(updater_folder)

    for file in update_infos["updater_files"]:
        if not os.path.exists(os.path.join(updater_folder, file)):
            logger.error(f"File {file} is missing in update, aborting update")
            tkinter.messagebox.showerror(
                title="Updater", message=f"File '{file}' is missing in updater !"
            )
            return
    return update_infos


def check_before_start() -> dict[str, dict] | None:
    logger.info("Checking stuff before starting update...")
    global installation_folder
    installation_folder = window.get_installation_folder()

    # Checking updater first
    try:
        results = check_update()

    except Exception:
        error = traceback.format_exc()
        logger.error(
            f"Unable to verify update due to the following error:\n{error}, aborting update"
        )
        tkinter.messagebox.showerror(
            title="Updater",
            message=f"Could not verifiy update validity due to the following error :\n{error}",
        )
        return

    else:
        if results:
            update_infos = results

            # Then checking installation
            try:
                results = check_installation(installation_folder, update_infos)

            except Exception:
                error = traceback.format_exc()
                logger.error(
                    f"Could not verifiy installation folder due to the following error :\n{error}\naborting update"
                )
                tkinter.messagebox.showerror(
                    title="Updater",
                    message=f"Could not verifiy installtion validity due to the following error :\n{error}",
                )

            else:
                if results:
                    installation_app_infos = results
                    return {
                        "installation_app_infos": installation_app_infos,
                        "update_infos": update_infos,
                    }

                else:
                    logger.error(
                        f"Selected folder {installation_folder} is not recognized as a valid books-quest installation, aborting update"
                    )
                    tkinter.messagebox.showerror(
                        title="Updater",
                        message="The selected folder is not recognized as a valid books-quest installation",
                    )


def try_cancel(update_res: utils.UpdateRes):

    try:
        cancel_update(update_res)

    except Exception:
        logger.error(
            f"Could not cancel update due to the following error:\n{traceback.format_exc()}"
        )
        window.update_error_sc.error = (
            window.update_error_sc.error
            + f"\n----- [UPDATE_CANCELATION_ERROR] -----:\n{traceback.format_exc()}"
        )
        tkinter.messagebox.showerror(
            title="Books Quest Updater",
            message=f"Could not cancel update, your installation may be corrupted !\nERROR :\n{traceback.format_exc()}",
        )
        window.update_error_sc.cancel_b.config(text="Quit", command=complete_exit)
        window.update_error_sc.error_lb.config(
            text="Sorry, an error has occured and the update could not be canceled\nyour installation may be corrupted"
        )
        window.wm_protocol("WM_DELETE_WINDOW", complete_exit)

    else:
        window.update_error_sc.error_lb.config(
            text="The update has been successfully canceled, you can close this window\nTo help us improve the service, you can report the error at https://github.com/SoloEnder/books-quest/issues"
        )
        window.switch_screen("update_error_screen")
        window.protocol("WM_DELETE_WINDOW", complete_exit)
        window.update_error_sc.cancel_b.config(text="Quit", command=complete_exit)
        tkinter.messagebox.showinfo(
            title="Books Quest Updater", message="Update canceled sucessfully"
        )


def cancel_update(update_res: utils.UpdateRes):
    logger.info("Cancelling update...")
    undo.run(update_res, window)
    update_res.update_state_data["status"] = "ABORTED"
    update_res.update_state_data["ended_at"] = str(dt.datetime.now())
    utils.write_json(update_res.update_state_filepath, update_res.update_state_data)
    clean.run(update_res.update_state_filepath, update_res)


def finish_update(
    update_res: utils.UpdateRes,
):
    logger.info("Finishing update...")
    try:
        update_state_data = update_res.update_state_data
        installation_infos = update_res.installation_infos
        update_state_data["state"] = "COMPLETED"
        update_state_data["ended_at"] = str(dt.datetime.now())
        app_current_version = installation_infos.get(
            "app_version", update_res.installation_app_infos["app_version"]
        )
        installation_infos["app_version"] = update_state_data["update_to"]
        installation_infos["previous_versions"] = installation_infos.get(
            "previous_versions", []
        )
        installation_infos["previous_versions"].append(app_current_version)
        installation_infos["last_update_date"] = update_state_data["ended_at"]

        installation_infos["boots_count"] = installation_infos.get("boots_count", 0)
        installation_infos_filepath = os.path.join(
            update_res.installation_folder,
            "app",
            "data",
            "app_data",
            "installation_infos.json",
        )
        utils.write_json(installation_infos_filepath, installation_infos)
        utils.write_json(update_res.update_state_filepath, update_state_data)
        clean.run(update_res.update_state_filepath, update_res)

    except Exception:
        logger.error(
            f"Could not finish update, due to the following error:\n{traceback.format_exc()}"
        )
        window.update_error_sc.error = traceback.format_exc()
        window.update_error_sc.cancel_b.config(
            command=lambda: cancel_update(update_res)
        )
        window.switch_screen("update_error_screen")

    else:
        window.wm_protocol("WM_DELETE_WINDOW", complete_exit)
        window.switch_screen("update_success_screen")


def some_compatibility(installation_app_infos: dict):
    if installation_app_infos.get("version"):
        installation_app_infos["app_version"] = installation_app_infos["version"][
            "readable"
        ]

    if not installation_app_infos.get("elements_to_preserve"):
        installation_app_infos["elements_to_preserve"] = [
            "app/data/books_data",
            "app/data/bookshelves_data",
            "app/logs",
        ]

    logger.info(
        f"App version after compatibility operation is {installation_app_infos['app_version']}"
    )


def try_update():
    check_debris_mode(installation_folder=window.get_installation_folder())
    result = check_before_start()
    if not result:
        return

    installation_app_infos, update_infos = result.values()
    window.update_error_sc.cancel_b.config(command=sys.exit)
    if not utils.ishigher(installation_app_infos["app_version"], "0.2.0"):
        installation_app_infos["root_directory_content"] = [
            "app",
            "licenses",
            "THIRD_PARTY_NOTICE.txt",
            "LICENSE",
            "updater.exe",
            "books-quest.exe",
            "_internal",
        ]
        installation_app_infos["app_version"] = installation_app_infos["version"][
            "readable"
        ]
    backup_folder = os.path.join(
        installation_folder,
        f"backup_{''.join(installation_app_infos['app_version'].split('.'))}",
    )
    undo_filepath = os.path.join(backup_folder, "undo.json")
    update_state_filepath = os.path.join(
        installation_folder,
        "update_state.json",
    )
    excepted_installation_infos_path = os.path.join(
        installation_folder, "app", "data", "app_data", "installation_infos.json"
    )
    if os.path.exists(excepted_installation_infos_path):
        installation_infos = utils.read_json(excepted_installation_infos_path)

    else:
        installation_infos = {}
    update_state_data = {
        "started_at": str(start),
        "ended_at": None,
        "status": "IN_PROGRESS",
        "update_to": update_infos["update_to"],
        "backup_folder": backup_folder,
    }
    update_res = utils.UpdateRes(
        installation_folder,
        updater_folder,
        backup_folder,
        update_state_filepath,
        undo_filepath,
        installation_infos,
        installation_app_infos,
        update_infos,
        update_state_data,
        "INSTALLATION",
        "UPDATE",
        "BACKUP",
    )
    logger.info("Writing update state data...")
    utils.write_json(update_state_filepath, update_state_data, True)
    logger.info("Creating update backup folder...")
    utils.check_and_make_folder(backup_folder)
    logger.info("Writing undo.json for the first time...")
    utils.write_json(undo_filepath, [])
    update_actions_handler = utils.UpdateActionsHandler(update_res, window)
    migrations_handler = migrate.MigrationsHandler(
        update_res, update_actions_handler, window
    )
    logger.info("Finding migrations...")
    migrations_handler.find_migration()
    try:
        window.wm_protocol("WM_DELETE_WINDOW", no_exit)
        applier.run(
            update_res,
            update_actions_handler,
            window,
        )
        logger.info("Applying migrations...")
        migrations_handler.apply_migrations()
        logger.info("Restoring preserved elements...")
        update_actions_handler.restore_preserved_elements()

    except Exception:
        logger.error(
            f"Could not apply update due to the following error :\n{traceback.format_exc()}"
        )
        window.update_error_sc.error = (
            f"----- [UPDATE_ERROR] -----:\n{traceback.format_exc()}"
        )
        window.update_error_sc.cancel_b.config(command=lambda: try_cancel(update_res))
        window.wm_protocol(
            "WM_DELETE_WINDOW",
            lambda: try_cancel(update_res),
        )
        window.switch_screen("update_error_screen")

    else:
        finish_update(update_res)


start = dt.datetime.now()
mode_parser = argparse.ArgumentParser(add_help=False)
mode_parser.add_argument(
    "-m",
    "--mode",
    choices=["update", "finish-update", "check-debris"],
    help="The mode in which the updater should run",
    default="update",
)
mode_arg, unknown_args = mode_parser.parse_known_args()


window = gui.Window()
window.updater_version = VERSION
updater_file = sys.executable
updater_folder = str(pathlib.Path(updater_file).parent.resolve())


def update_mode():
    logger.info("Starting 'update' mode")
    installation_folder_parser = argparse.ArgumentParser(parents=[mode_parser])
    installation_folder_parser.add_argument(
        "-i",
        "--installation_folder",
        help="The path to the installation to update",
    )
    installation_folder_arg = installation_folder_parser.parse_args()

    if installation_folder_arg.installation_folder:
        window.installation_selection_sc.installation_path_sv.set(
            installation_folder_arg.installation_folder
        )
        window.withdraw()
        try_update()

    else:
        window.installation_selection_sc.confirm_b.config(command=try_update)


def check_debris_mode(installation_folder: str = updater_folder):
    logger.info("Starting 'check-debris' mode")
    try:
        update_state_filepath = os.path.join(installation_folder, "update_state.json")

        if os.path.exists(update_state_filepath):
            logger.info("update_state.json file found, loading update state infos...")
            update_state_data = utils.read_json(update_state_filepath)

        else:
            logger.info("No update_state.json file found, canceling check-debris")
            update_state_data = {}
            return

        backup_folder = update_state_data["backup_folder"]

        if not os.path.exists(backup_folder):
            logger.info("No backup folder found, canceling check-debris")
            return

        undo_filepath = os.path.join(backup_folder, "undo.json")
        installation_app_infos_filepath = os.path.join(
            installation_folder, "app", "app_infos.json"
        )

        if os.path.exists(installation_app_infos_filepath):
            installation_app_infos = utils.read_json(installation_app_infos_filepath)

        else:
            installation_app_infos = {
                "app_version": "0.0.0",
                "elements_to_preserve": [],
                "root_directory_content": [],
            }
        some_compatibility(installation_app_infos)
        after_update_res = utils.UpdateRes(
            installation_folder,
            "",
            backup_folder,
            update_state_filepath,
            undo_filepath,
            {},
            installation_app_infos,
            {},
            update_state_data,
            "INSTALLATION",
            "UPDATE",
            "BACKUP",
        )
        if update_state_data["status"] == "IN_PROGRESS":
            logger.info("Update marked as in progress, cancelling update")
            tkinter.messagebox.showinfo(
                title="Updater",
                message="An incomplete update has been detected in your installation\nThis update must be canceled before performing any other action",
            )
            cancel_update(after_update_res)

    except Exception:
        tkinter.messagebox.showerror(
            title="Books-Quest Updater",
            message=f"Failed to check update debris due to the following exception :\n{traceback.format_exc()}",
        )
        window.update_error_sc.error = (
            f"----- [UPDATE_CANCELATION_ERROR] -----:\n{traceback.format_exc()}"
        )
        window.update_error_sc.error_lb.config(
            text="Sorry, an error occured and the update could not be canceled sucessfully\nYour installation may be corrupted !"
        )
        window.update_error_sc.cancel_b.config(
            text="Quit", command=lambda: complete_exit(1)
        )
        window.switch_screen("update_error_screen")

    else:
        logger.info("Mode check-debris completed successfully")


def complete_exit(exit_code: int = 0):
    window.destroy()
    sys.exit(exit_code)


if mode_arg.mode == "update":
    logger.info("Launching in 'update' mode")
    update_mode()

elif mode_arg.mode == "check-debris":
    logger.info("Launching in 'check-debris' mode")
    check_debris_mode()
    complete_exit()

window.mainloop()
