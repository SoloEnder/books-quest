from __future__ import annotations

import logging
import webbrowser

from PySide6 import QtCore, QtWidgets

from app.src import langs_handler, resources_handler, settings_handler
from app.ui import qt_signals_handler
from app.ui.main_pages import base_page
from app.utils import utils_funcs


class SettingsPage(base_page.BasePage):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        res_handler: resources_handler.RessourcesHandler,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(
            parent, res_handler, settings_handler, langs_handler, qt_signals_handler
        )
        self.logger = logging.getLogger()
        self.PAGE_NAME = "SETTINGS_PAGE"
        self.nav_bar = MainNavigationBar(None)
        self.main_lyt.addWidget(self.nav_bar)
        self.setObjectName("settings_page")
        utils_funcs.load_and_set_ss(
            self.res_handler.get_res("assets.qss.settings_page"),
            widget=self,
            logger=self.logger,
        )

        # ---- The dictionnary which contains the page object ----
        self._sections = {}

        # ---- The widgets which display the differents settings sections ----
        self._sections_displayer = QtWidgets.QStackedWidget()

        # ---- Creating and adding the differents settings sections ----
        self.nav_bar.section_requested_sg.connect(
            self.set_displayed_section
        )  # The naviguation bar
        self.appearance_settings = AppearanceSettings(
            None, self.settings_handler, self.langs_handler, self.qt_signals_handler
        )
        self.update_settings = UpdateSettings(
            None, self.settings_handler, self.langs_handler, self.qt_signals_handler
        )
        self.about_settings = AboutSettings(
            None, self.settings_handler, self.langs_handler, self.qt_signals_handler
        )
        self.about_button = QtWidgets.QPushButton("About")
        self.about_button.clicked.connect(
            lambda: self.qt_signals_handler.show_about_sg.emit(True)
        )

        self.apply_button = QtWidgets.QPushButton(
            self.langs_handler.tr("shared.actions.done")
        )
        self.apply_button.clicked.connect(self.apply_and_refresh)
        self.add_section(
            self.appearance_settings,
            self.langs_handler.tr("settings.general.appearance.section_title"),
        )
        self.add_section(
            self.update_settings,
            self.langs_handler.tr("settings.general.update.section_title"),
        )
        self.add_section(
            self.about_settings,
            self.langs_handler.tr("settings.general.about.section_title"),
        )

        self.main_lyt.addWidget(self.nav_bar, 0, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.main_lyt.addWidget(
            self._sections_displayer, 0, 1, 2, 1, QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.main_lyt.addWidget(self.about_button, 1, 0)
        self.main_lyt.addWidget(self.apply_button, 2, 0)

    def apply_and_refresh(self):
        """
        Send a signal to all SettingsSection to save the settings, and emit the signal to refresh UI
        """
        self.logger.info("Applying new settings...")
        self.qt_signals_handler.edit_progress_msg.emit(
            self.langs_handler.tr("settings.msg.applying_changes")
        )
        self.logger.debug("Sending new settings save request...")
        self.qt_signals_handler.apply_settings_sg.emit()
        self.logger.debug("Sending UI refresh request...")
        self.qt_signals_handler.refresh_ui_sg.emit()
        self.qt_signals_handler.edit_progress_msg.emit(" ")
        QtWidgets.QMessageBox.information(
            None, "Settings", self.langs_handler.tr("settings.msg.settings_updated")
        )

    def has_section(self, section: SettingsSection) -> bool:
        """
        Check if `section` is integrated to this SettingsHandler.
        Return True if this is the case, otherwise False.

        Parameters
        ----------
        section (SettingsSection): the section to check

        Returns
        -------
        bool: if the section is integrated or not

        Details
        -------
        This method first check if the section.SECTION_NAME attribute is a key of the `_sections` dict attribute,
        then check if the `section` value in the dict is the same object as the `section` parameter.
        """
        if section.SECTION_NAME in self._sections.keys():
            if self._sections[section.SECTION_NAME] == section:
                return False

            else:
                return True
        else:
            return False

    def has_section_with_name(self, section_name: str) -> bool:
        """
        This method checks if `section_name` is a key of `_sections` attribute
        Return True if yes, otherwise False
        """
        if section_name in self._sections.keys():
            return True
        else:
            return False

    def add_section(self, section: SettingsSection, nav_button_text: str):
        """
        Integrate a new `SettingsSection` instance to this `SettingsHandler`

        Parameters
        ----------
        section: an instance of `SettingsSection`
        nav_button_text: The button displayed on the naviguation button for this section
        """
        if not self.has_section(section):
            self._sections[section.SECTION_NAME] = section
            self._sections_displayer.addWidget(section)
            self.nav_bar.add_section_button(section.SECTION_NAME, nav_button_text)

        else:
            raise ValueError(
                f"A SettingsSection named '{section.SECTION_NAME} is already integrated !'"
            )

    def remove_section(self, section: SettingsSection):
        """
        Integrate a new `SettingsSection` instance to this `SettingsHandler`
        """
        if self.has_section(section):
            del self._sections[section.SECTION_NAME]
            self.nav_bar.remove_section_button(section.SECTION_NAME)

        else:
            raise ValueError(
                f"Section with name '{section.SECTION_NAME}' not integrated to this SettingsPage!'"
            )

    def set_displayed_section(self, section_name: str):
        """
        Set the currently displayed settings section to the one at `section_name`

        Raises
        ------
        ValueError: if no settings sectioon with this name is found
        """
        if self.has_section_with_name(section_name):
            self._sections_displayer.setCurrentWidget(self._sections[section_name])

        else:
            raise ValueError(f"Unknown section name : '{section_name}'")


class SettingsSection(QtWidgets.QWidget):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        section_name: str,
        header_lang_path: str,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(parent)
        self.SECTION_NAME = section_name
        self.header_lang_path = header_lang_path
        self.settings_handler = settings_handler
        self.langs_handler = langs_handler
        self.qt_signals_handler = qt_signals_handler

        self.base_lyt = QtWidgets.QGridLayout()
        self.setLayout(self.base_lyt)

        self._child_sections: dict[str, SettingsSection] = {}

        self.header_lb = QtWidgets.QLabel(self.langs_handler.tr(header_lang_path))
        self.header_lb.setProperty("role", "h2")
        self.base_lyt.addWidget(self.header_lb, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)

        # --- Connecting the signal emitted when an appliance of the new settings is request
        self.qt_signals_handler.apply_settings_sg.connect(self.apply_settings)

    def has_child_section(self, section: SettingsSection) -> bool:
        """
        Check if `section` is a child of this SettingsSection.
        Return True if this is the case, otherwise False.

        Parameters
        ----------
        section (SettingsSection): the section to check

        Returns
        -------
        bool: if  `section` is a child or not

        Details
        -------
        This method first check if the section.SECTION_NAME attribute is a key of the `_child_sections` dict attribute,
        then check if the `section` value in the dict is the same object as the `section` parameter.
        """
        if section.SECTION_NAME in self._child_sections.keys():
            if self._child_sections[section.SECTION_NAME] == section:
                return True

            else:
                return False

        else:
            return False

    def set_header_text(self, text: str):
        self.header_lb.setText(text)

    def add_child_section(self, section: SettingsSection):
        """
        Add `section` as a child section of this SettingsSection
        """
        self._child_sections[section.SECTION_NAME] = section
        self.base_lyt.addWidget(section)

    def apply_settings(self):
        """
        This is where must be the recuperation and the appliance of the new settings value
        """


class GeneralSettings(SettingsSection):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(
            parent,
            "General",
            "settings.general.section_title",
            settings_handler,
            langs_handler,
            qt_signals_handler,
        )


class AppearanceSettings(SettingsSection):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(
            parent,
            "APPEARANCE",
            "settings.general.appearance.section_title",
            settings_handler,
            langs_handler,
            qt_signals_handler,
        )
        self.header_lb.setStatusTip(
            self.langs_handler.tr("settings.general.appearance.section_description")
        )
        self.header_lb.setProperty("role", "h3")
        self.langs_settings = LangsSettings(
            None,
            settings_handler,
            self.langs_handler,
            qt_signals_handler,
        )
        self.add_child_section(self.langs_settings)


class LangsSettings(SettingsSection):
    """
    The SettingsSection for the languages options
    """

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        settings_handler: settings_handler.SettingsHandler,
        langs_handler: langs_handler.LangsHandler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(
            parent,
            "LANGS_SETTINGS",
            "settings.general.appearance.language.section_title",
            settings_handler,
            langs_handler,
            qt_signals_handler,
        )
        self.header_lb.setProperty("role", "h4")
        self.header_lb.setStatusTip(
            self.langs_handler.tr(
                "settings.general.appearance.language.section_description"
            )
        )

        # --- The widgets for the language selection
        self.lang_selection_lb = QtWidgets.QLabel(
            self.langs_handler.tr(
                "settings.general.appearance.language.edit_current_lang"
            )
        )
        self.lang_selection_combob = QtWidgets.QComboBox()
        self.languages_opts_indexes = {
            "fr": 0,
            "en": 1,
        }
        self.lang_selection_combob.addItem("Français", "fr")
        self.lang_selection_combob.addItem("English", "en")
        self.lang_selection_combob.setCurrentIndex(
            self.languages_opts_indexes[
                str(
                    self.settings_handler.get_setting_value(
                        "general.appearance.language"
                    )
                )
            ]
        )
        self.base_lyt.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.base_lyt.addWidget(
            self.lang_selection_lb,
            1,
            0,  # QtGui.Qt.AlignmentFlag.AlignLeft
        )
        self.base_lyt.addWidget(
            self.lang_selection_combob,
            1,
            1,  # QtGui.Qt.AlignmentFlag.AlignLeft
        )

    def apply_settings(self):
        self.settings_handler.set_setting_value(
            "general.appearance.language",
            self.lang_selection_combob.currentData(),
        )


class UpdateSettings(SettingsSection):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        settings_handler,
        langs_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(
            parent,
            "update_settings",
            "settings.general.update.section_title",
            settings_handler,
            langs_handler,
            qt_signals_handler,
        )
        self.header_lb.setProperty("role", "h3")
        self.header_lb.setStatusTip(
            self.langs_handler.tr("settings.general.update.section_description")
        )
        self.check_update_b = QtWidgets.QPushButton(
            self.langs_handler.tr("settings.general.update.actions.check_update")
        )
        self.check_update_b.clicked.connect(
            lambda: webbrowser.open_new_tab(
                "https://github.com/SoloEnder/books-quest/releases"
            )
        )
        self.check_update_b.setObjectName("check_update_button")
        self.check_update_b.setSizePolicy(QtWidgets.QSizePolicy())
        self.base_lyt.addWidget(
            self.check_update_b, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )


class AboutSettings(SettingsSection):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        settings_handler,
        langs_handler,
        qt_signals_handler: qt_signals_handler.QtSignalsHandler,
    ):
        super().__init__(
            parent,
            "about_settings",
            "settings.general.about.section_title",
            settings_handler,
            langs_handler,
            qt_signals_handler,
        )
        self.header_lb.setProperty("role", "h3")
        self.header_lb.setStatusTip(
            self.langs_handler.tr("settings.general.about.section_description")
        )
        self.about_bq_pb = QtWidgets.QPushButton("About Books Quest")
        # self.about_bq_pb.clicked.connect(lambda: self.qt_signals_handler.show_about_sg.emit(True))
        # self.about
        self.about_qt_pb = QtWidgets.QPushButton("About Qt")
        self.version_lb = QtWidgets.QLabel(
            self.langs_handler.tr(
                "settings.general.about.current_version", version="0.1.0"
            )
        )
        self.base_lyt.addWidget(
            self.version_lb, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft
        )


class MainNavigationBar(QtWidgets.QWidget):
    # --- Signal is emitted when the click on ones of the section's button in the naviguation bar ---
    section_requested_sg = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None):
        super().__init__(parent)
        self.lyt = QtWidgets.QVBoxLayout()
        self._sections_buttons: dict[str, QtWidgets.QPushButton] = {}
        self.setLayout(self.lyt)

    def has_button_for_section(self, section_name: str) -> bool:
        """
        Checks if there is a button for `section_name`, return True if yes, otherwise return False
        """

        if section_name in self._sections_buttons.keys():
            return True

        else:
            return False

    def add_section_button(self, section_name: str, displayed_text: str):
        """
        Add a new button for naviguate to a settings section with `section_name`

        Parameters
        ----------
        section_name: the name of the section to naviguate
        displayed_text: the text displayed on the button

        Raises
        ------
        ValueError: if `section_name` is already assigned to a button
        """

        if section_name not in self._sections_buttons.keys():
            button = QtWidgets.QPushButton(displayed_text)
            button.setProperty("role", "nav_button")
            button.clicked.connect(lambda: self.section_requested_sg.emit(section_name))
            self._sections_buttons[section_name] = button
            self.lyt.addWidget(button)

        else:
            raise ValueError(f"A section button for {section_name} already exists")

    def remove_section_button(self, section_name: str):
        """
        Removes the naviguation button for `section_name`

        Raises
        ------
        ValueError: if `section_name` is not assigned to a button
        """

        if section_name in self._sections_buttons.keys():
            self.lyt.removeWidget(self._sections_buttons[section_name])
            del self._sections_buttons[section_name]

        else:
            raise ValueError(f"Unknown section name {section_name}")
