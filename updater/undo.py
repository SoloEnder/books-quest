import logging
import os
import subprocess
import sys
import time
import tkinter.messagebox

import gui
import utils

logger = logging.getLogger("updater.undo")


class UndoActionsHandler(utils.UpdateActionsHandler):
    def __init__(
        self,
        update_res: utils.UpdateRes,
        window: gui.Window,
        undo_data: list | None = None,
    ):
        super().__init__(update_res, window, undo_data)

    def prepare_updater_replacement(
        self,
        updater_to_replace: str,
        new_updater: str,
        **kwargs,
    ):
        """
        Replace an updater by a new one.
        If the updater to replace is the currently being running updater,
        then the running  updater is duplicated (under a new name), then the duplicated version is launched and the running updater is closed.
        Otherwise, this method does the same as `remove() + copy()`

        Parmeters
        ---------
        - updater_to_replace: the path to the updater to replace
        - new_updater: the path to the new updater

        Returns
        -------
        - bool: if an exit of the current program is need or not
        """
        logger.info(
            f"Preparing the replacement of the updater at {updater_to_replace} by updater at {new_updater}..."
        )
        updater_to_replace_abs_path = utils.get_abs_path(
            updater_to_replace, self.update_res
        )

        if updater_to_replace_abs_path != sys.executable:
            logger.info(
                "Updater to replace is not the currently running updater, using COPY + REMOVE instead of REPLACE_UPDATER"
            )
            self.remove_element(updater_to_replace, backup=False)
            self.copy(from_=new_updater, to=updater_to_replace, add_undo=False)
            return False

        updater_to_replace_filename, updater_to_replace_ext = os.path.splitext(
            updater_to_replace_abs_path
        )
        duplicated_updater_path = f"{self.update_res.installation_alias}::{updater_to_replace_filename}.replace{updater_to_replace_ext}"
        self.copy(
            updater_to_replace,
            duplicated_updater_path,
            ignore_updater=True,
            add_undo=False,
        )
        self.add_undo(
            {
                "type": "REPLACE_UPDATER",
                "old_updater": updater_to_replace,
                "new_updater": new_updater,
            }
        )
        subprocess.Popen(
            [
                utils.get_abs_path(duplicated_updater_path, self.update_res),
                "-m",
                "check-debris",
            ]
        )
        return True

    def replace_updater(self, old_updater: str, new_updater: str, **kwargs):
        """
        Replace an updater file by another.
        May fail if the updater to replace is the currently being runned updater

        Parameters
        ----------
        old_updater (str): the path to the updater to replace
        new_updater (str): the path to the replacement updater
        """
        os.replace(
            utils.get_abs_path(new_updater, self.update_res),
            utils.get_abs_path(old_updater, self.update_res),
        )

    def apply_undo_instructions(
        self,
        ignore_unknown: bool = True,
    ):
        """
        Apply a list of update instructons (like REMOVE, to permanently or not remove an element, COPY to copy an element, etc)

        Parameters
        ----------
        - instructions: a list of instructions to do on files
        - ignore_unknown (bool=True): whether to ignore unknown instruction (otherwise, this will raise an `InvalidUpdateInstructionError`)
        - add_undo (bool=True): wheter to add an undo each instruction.
        """
        self.window.work_in_progress_sc.add_operations_group(
            "undo_update",
            "Undoing update changes...",
            operations_count=len(self.undo_data),
            set_as_current=True,
        )
        self.window.switch_screen("work_in_progress_screen")
        for instruction in self.undo_data.copy():
            if instruction["type"] == "REMOVE":
                self.remove_element(**instruction)
                self.done_undo(instruction)

            elif instruction["type"] == "COPY":
                self.copy(**instruction)
                self.done_undo(instruction)

            elif instruction["type"] == "MKDIR":
                self.make_dir(**instruction)
                self.done_undo(instruction)

            elif instruction["type"] == "PREPARE_UPDATER_REPLACEMENT":
                need_exit = self.prepare_updater_replacement(**instruction)
                self.done_undo(instruction)

                if need_exit:
                    tkinter.messagebox.showinfo(
                        title="Updater",
                        message="The updater will restart to continue the update cancelation, simply click on 'ok'",
                    )
                    logger.info(
                        "Exiting current updater and launching other updater..."
                    )
                    sys.exit()

            elif instruction["type"] == "REPLACE_UPDATER":
                logger.info(
                    "Waiting 5 seconds before replacing updater to make sure that the updater to replace properly exit..."
                )
                time.sleep(5)
                self.replace_updater(**instruction)
                self.done_undo(instruction)

            else:
                if not ignore_unknown:
                    raise utils.InvalidUpdateInstructionError(
                        f"Unknwon undo instruction type : '{instruction['type']}'"
                    )
            self.window.work_in_progress_sc.progress_group()

    def done_undo(self, undo_instruction, undo_filepath: str | None = None):
        self.undo_data.remove(undo_instruction)
        self.save_undo_data(undo_filepath)


def run(after_update_res: utils.UpdateRes, window: gui.Window):
    window.work_in_progress_sc.add_operations_group(
        "update_cancel", "Canceling update...", set_as_current=True
    )
    window.switch_screen("work_in_progress_screen")
    undo_actions_handler = UndoActionsHandler(after_update_res, window)
    logger.info(
        f"Loading undo data from {undo_actions_handler.update_res.undo_filepath}"
    )
    undo_actions_handler.load_undo_data()
    logger.info("Undoing update changes...")
    undo_actions_handler.apply_undo_instructions()
