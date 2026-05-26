from io import BytesIO
import speech_recognition as sr
from .base import BaseSpeechEngine


class SpeechRecognitionGoogleEngine(BaseSpeechEngine):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe(self, audio_segment, idioma):
        buffer = BytesIO()
        audio_segment.export(buffer, format="wav")
        buffer.seek(0)

        with sr.AudioFile(buffer) as source:
            audio_data = self.recognizer.record(source)

        try:
            return self.recognizer.recognize_google(
                audio_data,
                language=idioma
            )

        except sr.UnknownValueError:
            return ""

        except sr.RequestError as e:
            raise RuntimeError(f"SpeechRecognition API falhou: {e}")
