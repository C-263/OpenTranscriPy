import whisper
import numpy as np
import torch

from .base import BaseSpeechEngine
from transcriber.speech.resolver.whisper_resolver import resolve_whisper_model
from transcriber.speech.resolver.model_safety import ModelSafety


class WhisperEngine(BaseSpeechEngine):

    def __init__(self, model_config=None):
        self.model_config = model_config or {}

        model_type = self.model_config.get("model_type", "small")
        self.confirm = self.model_config.get("confirm", False)

        # 🔥 trava de segurança (medium/large)
        safety = ModelSafety.require_confirmation("whisper", model_type)

        if safety["require_confirmation"] and not self.confirm:
            raise PermissionError(
                f"{safety['reason']} | use confirm=True"
            )

        self.model_name = resolve_whisper_model(model_type)

        print(f"🔄 Carregando Whisper: {self.model_name}")
        self.model = whisper.load_model(self.model_name)

    def transcribe(self, audio_segment, idioma=None):
        samples = np.array(audio_segment.get_array_of_samples())

        if audio_segment.sample_width == 2:
            samples = samples.astype(np.float32) / 32768.0
        else:
            samples = samples.astype(np.float32)

        if audio_segment.channels > 1:
            samples = samples.reshape((-1, audio_segment.channels))
            samples = samples.mean(axis=1)

        try:
            result = self.model.transcribe(
                samples,
                language=idioma.split("-")[0] if idioma else None
            )

            return result.get("text", "").strip()

        finally:
            del samples

            if torch.cuda.is_available():
                torch.cuda.empty_cache()