from .engines import *

_DEFAULT_IDIOMA = "pt-br"


class SpeechEngine:
    def __init__(self, engine_name: str = "vosk", model_config: dict = None):
        self.model_config = model_config or {}
        self.engine = self._load_engine(engine_name)

    def _load_engine(self, name: str):
        if name == "vosk":
            return VoskEngine(self.model_config)
        elif name == "whisper":
            return WhisperEngine(self.model_config)
        elif name == "faster_whisper":
            return FasterWhisperEngine(self.model_config)
        elif name == "speech_recognition":
            return SpeechRecognitionGoogleEngine()
        else:
            raise ValueError(f"Engine '{name}' não suportada")


    def transcribe(self, audio_segment, idioma: str = None):
        idioma = idioma or self.model_config.get("idioma", _DEFAULT_IDIOMA)
        model_type = self.model_config.get("model_type", "small")
        with_words = self.model_config.get("with_words", False)

        if isinstance(self.engine, VoskEngine):
            if with_words and hasattr(self.engine, "transcribe_with_words"):
                return self.engine.transcribe_with_words(
                    audio_segment, idioma=idioma, model_type=model_type,
                )
            return self.engine.transcribe(
                audio_segment, idioma=idioma, model_type=model_type,
            )

        if isinstance(self.engine, FasterWhisperEngine):  # ← bloco novo
            return self.engine.transcribe(audio_segment, idioma=idioma)

        return self.engine.transcribe(audio_segment, idioma=idioma)