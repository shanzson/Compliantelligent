from deep_translator import GoogleTranslator
import solidityscan_agent.config as config

"""
    translates error message to specified language in constants.py (ERROR_LANGUAGE_CODE var).
    both the key and value is translated and returned.
    default language is English.
"""
class ErrorLanguageMapper:
    def get_translation_language(self):
        pass

    def __init__(self) -> None:
        self.language = config.Config().get_config_value("error_language") or "en"

    def translate(self, text):
        try:
            translated_obj = {}
            for key in text:
                temp_text_key = key
                key = GoogleTranslator(source="auto", target=self.language).translate(key)
                translated_obj[key] = GoogleTranslator(source="auto", target=self.language).translate(text[temp_text_key])

            return translated_obj
        except Exception:
            return text
