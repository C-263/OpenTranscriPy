import gc
import os
import time
from transcriber.speech.speech_engine import SpeechEngine


class AudioProcessor:
    def __init__(
        self,
        engine: str = "vosk",
        model_config: dict = None
    ):
        self.engine = engine
        self.model_config = model_config or {}

        self.speech = SpeechEngine(
            engine_name=self.engine,
            model_config=self.model_config,
        )

    def process_chunk(self, i, audio_chunk, offset_ms, idioma):
        start_time = time.perf_counter()
        timestamp = self.seconds_to_hms(offset_ms / 1000)

        try:
            if audio_chunk is None or len(audio_chunk) == 0:
                result = "[Erro: áudio vazio]"
            else:
                result = self.speech.transcribe(audio_chunk, idioma)

            result = self._extract_text(result)

            if not result.strip():
                result = "[Erro: não reconhecido]"

        except Exception as e:
            result = f"[Erro: {e}]"

        final_text = f"[{timestamp}] {result.strip()}"
        duration = time.perf_counter() - start_time
        print(f"🎧 Bloco {i + 1} concluído em {duration:.2f}s")

        del audio_chunk
        gc.collect()
        return i, final_text, duration

    def build_final_transcription(self, pasta="transcription_chunks"):
        files = sorted(
            f for f in os.listdir(pasta)
            if f.startswith("bloco_") and f.endswith(".txt")
        )
        final_text = []
        for file_name in files:
            with open(os.path.join(pasta, file_name), "r", encoding="utf-8") as f:
                final_text.append(f.read().strip())
        return "\n".join(final_text)

    @staticmethod
    def _extract_text(result) -> str:
        if isinstance(result, dict):
            return result.get("text", "")
        return result or ""

    @staticmethod
    def seconds_to_hms(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02}"