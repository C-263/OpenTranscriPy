from vosk import Model, KaldiRecognizer
import json
import wave
from io import BytesIO
from transcriber.config.paths import VOSK_PATH
from .base import BaseSpeechEngine
from transcriber.speech.resolver.vosk_resolver import resolve_vosk_model


class VoskEngine(BaseSpeechEngine):
    _models_cache = {}

    def __init__(self, model_config=None):
        self.model_config = model_config or {}
        self.model = None
        self.model_path = None

    def _load_model(self, model_path: str):
        if model_path not in self._models_cache:
            print(f"🔄 Carregando modelo Vosk: {model_path}")
            self._models_cache[model_path] = Model(model_path)
        self.model = self._models_cache[model_path]
        self.model_path = model_path

    def _ensure_model(self, idioma: str, model_type: str):
        model_type = model_type or self.model_config.get("size", "small")
        model_info = resolve_vosk_model(
            lang=idioma,
            model_type=model_type,
            base_path=VOSK_PATH
        )
        self._load_model(model_info)

    def _create_recognizer(self, wf, with_words: bool = False):
        rec = KaldiRecognizer(self.model, wf.getframerate())
        rec.SetWords(with_words)
        return rec

    def _process_audio(self, rec, wf):
        results = []
        while True:
            data = wf.readframes(4000)
            if not data:
                break
            if rec.AcceptWaveform(data):
                results.append(json.loads(rec.Result()))
        results.append(json.loads(rec.FinalResult()))
        return results

    def _audiosegment_to_wave(self, audio_segment):
        buffer = BytesIO()
        audio_segment.export(buffer, format="wav")
        buffer.seek(0)
        return wave.open(buffer, "rb")

    def transcribe(self, audio_segment, idioma: str = "pt-br", model_type: str = "small",) -> str:
        wf = self._audiosegment_to_wave(audio_segment)
        self._ensure_model(idioma, model_type)
        rec = self._create_recognizer(wf)
        results = self._process_audio(rec, wf)
        return " ".join(r.get("text", "") for r in results).strip()

    # -------------------------
    # TRANSCRIBE WITH WORDS
    # -------------------------
    def transcribe_with_words(self, audio_segment, idioma: str = "pt-br", model_type: str = "small",) -> dict:
        wf = self._audiosegment_to_wave(audio_segment)
        self._ensure_model(idioma, model_type)
        rec = self._create_recognizer(wf, with_words=True)
        results = self._process_audio(rec, wf)

        words = []
        text = []
        for r in results:
            if "result" in r:
                words.extend(r["result"])
            if "text" in r:
                text.append(r["text"])

        return {
            "text": " ".join(text).strip(),
            "words": words,
        }