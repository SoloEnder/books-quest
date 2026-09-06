import logging

from app.src.services import qt_signals, res_files, settings


class UnsupportedLanguageError(Exception):
    def __init__(self, language: str) -> None:
        self.language = language
        self.msg = (
            f"Language '{self.language}' is unknown or not supported by the app !"
        )

    def __str__(self) -> str:
        return self.msg


class LangsService:
    def __init__(
        self,
        res_files: res_files.ResourcesFilesService,
        settings: settings.SettingsService,
        qt_signals: qt_signals.QtSignalsService,
    ):
        """
        Various language features
        """
        self.res_files = res_files
        self.settings = settings
        self.qt_signals = qt_signals

        self.logger = logging.getLogger(f"{__name__}-LangsService")
        self.logger.info("Settings Service initialized")

    def set_language(self, language: str, send_refresh_request: bool = True):
        """
        Set the app current language to `language`

        Parameters
        ----------
        - send_refresh_request: whether to emit a REFRESH_UI signal
        """
        available_languages = self.settings.get_setting_choices(
            "general.appearance.language"
        )
        lowered_language = language.lower()

        # Language unknown/unsupported
        if lowered_language not in available_languages:
            raise UnsupportedLanguageError(language)

        self.settings.set_setting_value("general.appearance.language", language)

        if send_refresh_request:
            self.qt_signals.emit_signal("refresh_ui_sg")
