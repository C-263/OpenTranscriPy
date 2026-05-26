from abc import ABC, abstractmethod

class BaseSpeechEngine(ABC):

    @abstractmethod
    def transcribe(self, audio_segment, idioma):
        pass
