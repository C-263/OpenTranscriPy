# Whisper / Faster Whisper / SpeechRecognition — ISO 639-1 (dois caracteres)
# https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
WHISPER_LANG_MAP: dict[str, tuple[str, str]] = {
    "1":  ("pt", "Português"),
    "2":  ("en", "English"),
    "3":  ("es", "Español"),
    "4":  ("fr", "Français"),
    "5":  ("de", "Deutsch"),
    "6":  ("it", "Italiano"),
    "7":  ("ja", "Japanese"),
    "8":  ("zh", "Chinese"),
    "9":  ("ru", "Russian"),
    "10": ("ar", "Arabic"),
    "11": ("ko", "Korean"),
    "12": ("nl", "Dutch"),
    "13": ("pl", "Polish"),
    "14": ("tr", "Turkish"),
    "15": ("uk", "Ukrainian"),
}

# Vosk — formato "ll-CC" (deve bater com o nome do modelo baixado)
# https://alphacephei.com/vosk/models
VOSK_LANG_MAP: dict[str, tuple[str, str]] = {
    "1":  ("pt-br", "Português (Brasil)"),
    "2":  ("en-us", "English (US)"),
    "3":  ("es",    "Español"),
    "4":  ("fr",    "Français"),
    "5":  ("de",    "Deutsch"),
    "6":  ("it",    "Italiano"),
    "7":  ("ja",    "Japanese"),
    "8":  ("zh",    "Chinese"),
    "9":  ("ru",    "Russian"),
    "10": ("ar",    "Arabic"),
    "11": ("ko",    "Korean"),
    "12": ("nl",    "Dutch"),
    "13": ("pl",    "Polish"),
    "14": ("tr",    "Turkish"),
    "15": ("uk",    "Ukrainian"),
}
