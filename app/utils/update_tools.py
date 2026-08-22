import logging

import requests
from PySide6 import QtWidgets

from app.src.langs_handler import LangsHandler

logger = logging.getLogger(__name__)


class UncomparablesVersionsError(Exception):
    """
    Usually raised when one version is not comparable to another/
    e.g. : version A is 1.2.3.4 but version B is 1.2.3 -> cannot be compared since they have not the same length
    Parameters
    ----------
    - version_a (str): the first version
    - version_b (str): the second version
    """

    def __init__(self, version_a: str, version_b: str):
        super().__init__()
        self.version_a = version_a
        self.version_b = version_b
        self.msg = f"Version {self.version_a} is not comparable with version {self.version_b} !"

    def __str__(self):
        return self.msg


def show_error(title: str | None = None, *, msg: str):
    QtWidgets.QMessageBox.critical(None, title or "Check for Updates", msg)


def get_latest_release_infos(url: str, langs_handler: LangsHandler) -> None | dict:
    logger.info(f"Getting latest release infos from {url}...")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

    except requests.Timeout:
        logger.error("Could not get app latest release infos : request timed out")
        show_error(
            msg=langs_handler.tr(
                "updates.errors.latest_release_infos.request_timed_out"
            )
        )
        return

    except requests.HTTPError as httperr:
        logger.error(f"Could not get app latest release infos : {httperr}")
        show_error(
            msg=langs_handler.tr(
                "updates.errors.latest_release_infos.httperr", httperr=httperr
            )
        )
        return

    except Exception:
        logger.exception("Unable to get latest release infos : ")
        show_error(msg=langs_handler.tr("updates.errors.unable_to_check_for_updates"))
        return

    return response.json()


def download_pop_up(release_infos: dict, title, msg, download_button_text: str):
    pop_up = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Icon.Information,
        title,
        msg,
        QtWidgets.QMessageBox.StandardButton.Cancel,
    )
    download_button = pop_up.addButton(
        download_button_text, QtWidgets.QMessageBox.ButtonRole.YesRole
    )
    pop_up.exec()
    return pop_up.clickedButton() == download_button


def is_higher_version(version_a: str, version_b: str) -> bool:
    """
    Checks whether `version_a` is higher than `version_b`

    Parameters
    ----------
    - version_a (str): the first version, in semver (major.minor.patch)
    - version_b (str): the version compared to, in semver (major.minor.patch)

    Returns
    -------
    - bool: wheter `version_a` version is higher than `version_b`
    """
    version_a_parts = version_a.split(".")
    version_b_parts = version_b.split(".")

    if len(version_a_parts) != len(version_b_parts):
        raise UncomparablesVersionsError(version_a, version_b)

    for index, version_a_part in enumerate(version_a_parts):
        version_a_part = int(version_a_part)
        version_b_part = int(version_b_parts[index])
        if version_a_part > version_b_part:
            return True

        elif version_a_part < version_b_part:
            return False

    return False
