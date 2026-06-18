from app.src import json_dicts_paths_handler, resources_handler


class LangsHandler(json_dicts_paths_handler.JSONDictPathHandler):
    def __init__(
        self, jfm, base_dict, res_handler: resources_handler.RessourcesHandler
    ):
        super().__init__(jfm, base_dict)
        self.res_handler = res_handler

    def set_current_language(self, language):
        """
        Set the current language to `language`
        """
        self.load_from_file(self.res_handler.get_res(f"assets.langs.{language}"))

    def tr(self, lang_dict_path: str, **kwargs):
        text = self.get_value(lang_dict_path)

        if isinstance(text, str):
            for kwarg, value in kwargs.items():
                text = text.replace(f"/f:<{kwarg}>/f", str(value))

            return text

        return str(None)
