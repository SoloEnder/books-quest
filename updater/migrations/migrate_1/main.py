# This file migrate from <= 0.2.0 to 0.3.0

import json
import logging
import os

import utils

logger = logging.getLogger(__name__)
MIGRATION_INFOS = {"application_range": ("0.1.0", "0.2.0"), "to": "0.3.0"}


def run(
    update_res: utils.UpdateRes,
    update_actions_handler: utils.UpdateActionsHandler,
):
    logger.info(
        f"Migrating data from {update_res.update_infos['update_to']} to {MIGRATION_INFOS['to']}"
    )
    data_folder = f"{update_res.installation_alias}::{os.path.join('app', 'data')}"
    modified_preserved_elements = []
    # ------ Old folder locations ------
    old_books_data_folder = (
        f"{update_res.backup_alias}::{os.path.join('app', 'data', 'books_data')}"
    )
    old_bookshelves_data_folder = (
        f"{update_res.backup_alias}::{os.path.join('app', 'data', 'bookshelves_data')}"
    )
    old_user_settings_filepath = f"{update_res.backup_alias}::{os.path.join('app', 'data', 'settings', 'user_settings.json')}"

    # ------ Folder where are stored the user data ------
    new_user_data_folder = os.path.join(data_folder, "user_data")
    new_books_data_folder = os.path.join(new_user_data_folder, "books_data")
    new_books_data_file = os.path.join(new_books_data_folder, "books.json")
    new_bookshelves_data_folder = os.path.join(new_user_data_folder, "bookshelves_data")
    new_bookshelves_data_file = os.path.join(
        new_bookshelves_data_folder, "bookshelves.json"
    )
    new_user_settings_filepath = os.path.join(
        new_user_data_folder, "user_settings.json"
    )

    update_actions_handler.make_dir(path=new_user_data_folder, exists_ok=True)

    if os.path.exists(utils.get_abs_path(old_books_data_folder, update_res)):
        update_actions_handler.copy(old_books_data_folder, new_books_data_folder)
        modified_preserved_elements.append("app/data/books_data")
        new_books_data_file_fullpath = utils.get_abs_path(
            new_books_data_file, update_res
        )
        if os.path.exists(new_books_data_file_fullpath):
            logger.info("Migrating books data...")
            migrate_covers_path(new_books_data_file_fullpath)

    if os.path.exists(utils.get_abs_path(old_bookshelves_data_folder, update_res)):
        update_actions_handler.copy(
            old_bookshelves_data_folder, new_bookshelves_data_folder
        )
        modified_preserved_elements.append("app/data/bookshelves_data")
        new_bookshelves_data_file_fullpath = utils.get_abs_path(
            new_bookshelves_data_file, update_res
        )
        if os.path.exists(new_bookshelves_data_file_fullpath):
            logger.info("Migrating bookshelves data...")
            migrate_covers_path(new_bookshelves_data_file_fullpath)

    if os.path.exists(utils.get_abs_path(old_user_settings_filepath, update_res)):
        update_actions_handler.copy(
            old_user_settings_filepath, new_user_settings_filepath
        )
        modified_preserved_elements.append("app/data/settings/user_settings")

    for element in modified_preserved_elements:
        update_actions_handler.remove_from_preserved_elements(element)


def migrate_covers_path(data_filepath: str):
    """
    Migrate the book data from the old to the new cover access system
    """

    try:
        objects: list[dict] = utils.read_json(data_filepath)

    except json.JSONDecodeError:
        logger.error(f"File '{data_filepath}' corrupted, aborting migration on it.")
        return

    for object in objects:
        if "cover_path" in object:
            del object["cover_path"]

    utils.write_json(data_filepath, objects)
