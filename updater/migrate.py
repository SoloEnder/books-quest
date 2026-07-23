import logging

import gui
import utils
from migrations.migrate_1 import main as mg1

logger = logging.getLogger("updater.migrate")

all_migrations = {
    "0.3.0": mg1,
}


class MigrationsHandler:
    def __init__(
        self,
        update_res: utils.UpdateRes,
        update_actions_handler: utils.UpdateActionsHandler,
        window: gui.Window,
    ):
        self.update_res = update_res
        self.update_actions_handler = update_actions_handler
        self.window = window
        self.elements_to_preserve: set = (
            self.update_actions_handler.elements_to_preserve
        )
        self.appliable_migrations = []

    def find_migration(self):
        self.window.work_in_progress_sc.add_operations_group(
            "find_migrations",
            "Searching for appliables data migrations...",
            operations_count=len(all_migrations),
            set_as_current=True,
        )
        self.window.switch_screen("work_in_progress_screen")
        for version, migration in all_migrations.items():
            logger.debug(
                f"Checking appliability of migration with infos={migration.MIGRATION_INFOS}..."
            )
            if utils.ishigher(
                version, self.update_res.installation_app_infos["app_version"]
            ):
                self.appliable_migrations.append(migration)
            self.window.work_in_progress_sc.progress_group()

        logger.info(f"Found {len(self.appliable_migrations)} appliable migrations")

    def apply_migrations(self):
        for migration in self.appliable_migrations:
            logger.info(f"Running migration with infos={migration.MIGRATION_INFOS}")
            migration.run(self.update_res, self.update_actions_handler)
