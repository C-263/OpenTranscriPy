import numpy as np
from faster_whisper import WhisperModel
from .base import BaseSpeechEngine
from transcriber.speech.resolver.whisper_resolver import resolve_whisper_model
from transcriber.speech.resolver.model_safety import ModelSafety


class FasterWhisperEngine(BaseSpeechEngine):
    def __init__(self, model_config=None):
        self.model_config = model_config or {}
        model_type = self.model_config.get("model_type", "small")
        self.confirm = self.model_config.get("confirm", False)
        self.beam_size = self.model_config.get("beam_size", 5)

        safety = ModelSafety.require_confirmation("faster-whisper", model_type)
        if safety["require_confirmation"] and not self.confirm:
            raise PermissionError(f"{safety['reason']} | use confirm=True")

        self.model_name = resolve_whisper_model(model_type)
        print(f"🔄 Carregando Faster-Whisper: {self.model_name}")

        use_cuda = self._has_cuda()
        self.model = WhisperModel(
            self.model_name,
            device="cuda" if use_cuda else "cpu",
            compute_type="float16" if use_cuda else "int8",
        )

    def transcribe(self, audio_segment, idioma=None) -> str:
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        samples /= 32768.0

        try:
            segments, _info = self.model.transcribe(
                samples,
                language=idioma.split("-")[0] if idioma else None,
                beam_size=self.beam_size,
            )
            return " ".join(seg.text for seg in segments).strip()
        finally:
            del samples

    def _has_cuda(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False