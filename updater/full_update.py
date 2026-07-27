import logging
import tkinter as tk

import utils

logger = logging.getLogger("updater.full_update")


def full_update(
    update_res: utils.UpdateRes,
    update_actions_handler: utils.UpdateActionsHandler,
    window: tk.Tk,
):
    logger.info("Generating full update instructions...")
    update_instructions = gen_instructions(update_res)
    logger.info("Starting full update...")
    update_actions_handler.apply_instructions(update_instructions)


def gen_instructions(update_res: utils.UpdateRes) -> list[dict[str, str]]:
    """
    Generate and return the update instructions that should bu used by the full updater.

    Parameters
    ----------
    update_res (UpdateRes): the handler of the update resources
    """
    instructions = []
    for element in update_res.installation_app_infos["root_directory_content"]:
        if element.endswith("updater.exe"):
            instructions.append(
                {
                    "type": "REMOVE",
                    "path": f"{update_res.installation_alias}::{element}",
                    "add_undo": False,
                }
            )
            continue
        instructions.append(
            {
                "type": "REMOVE",
                "path": f"{update_res.installation_alias}::{element}",
            }
        )

    for element in update_res.update_infos["update_root_directory_content"]:
        instructions.append(
            {
                "type": "COPY",
                "from_": f"{update_res.update_alias}::{element}",
                "to": f"{update_res.installation_alias}::{element}",
            }
        )

    return instructions
