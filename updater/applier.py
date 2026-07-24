import datetime as dt
import logging
import os
from tkinter import Tk

import full_update
import utils

logger = logging.getLogger("updater.applier")


class UnknownUpdateTypeError(utils.MyBaseException):
    def __init__(self, update_type):
        """
        Unknown update type
        """
        self.update_type = update_type
        self.msg = f"Unknown update type '{self.update_type}'"


def run(
    update_res: utils.UpdateRes,
    update_actions_handler: utils.UpdateActionsHandler,
    window: Tk,
):
    update_infos = update_res.update_infos
    utils.check_and_make_folder(update_res.backup_folder)
    update_state_data = {
        "started_at": str(dt.datetime.now()),
        "ended_at": None,
        "status": "IN_PROGRESS",
        "update_to": update_infos["update_to"],
        "backup_folder": update_res.backup_folder,
    }
    update_state_filepath = os.path.join(
        update_res.installation_folder, "update_state.json"
    )
    utils.write_json(update_state_filepath, update_state_data)
    if update_infos["type"] == "FULL_UPDATE":
        logger.info("Starting full update...")
        full_update.full_update(
            update_res,
            update_actions_handler,
            window,
        )

    else:
        raise UnknownUpdateTypeError(update_infos["type"])
