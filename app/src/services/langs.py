import functools
import logging

from dicts_paths_handler.dicts_paths_handler import DictsPathsHandler

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
        self.dicts_paths_handler = DictsPathsHandler()
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
        self.dicts_paths_handler.base_dict = self.res_files.read_indexed_file(
            f"assets.langs.{language}"
        )  # Loading the language file

        if send_refresh_request:
            self.qt_signals.emit_signal("refresh_ui_sg")

    @functools.cache  # Warning ingored, because these are singletons, instancied only at startup
    def tr(self, lang_dict_path: str, **kwargs):
        text = self.dicts_paths_handler.get_value(lang_dict_path)

        if isinstance(text, str):
            for kwarg, value in kwargs.items():
                text = text.replace(f"/f:<{kwarg}>/f", str(value))

            return text

        return ""
