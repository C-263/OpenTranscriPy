import math
import os
import subprocess
import tempfile

from pydub import AudioSegment

from .lazy_audio_parts import LazyAudioParts


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".flv",
    ".webm"
}


class AudioSplitter:

    def __init__(self, audio_file, chunk_duration_seconds=30):

        self.audio_file = os.path.normpath(audio_file)
        self.chunk_duration_seconds = chunk_duration_seconds

        self._extract_audio_if_video()

        self._chunks = self._build_chunks_metadata()

    def _extract_audio_if_video(self):

        ext = os.path.splitext(self.audio_file)[1].lower()

        if ext not in VIDEO_EXTENSIONS:
            return

        output = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ).name

        print("🎬 Extraindo áudio do vídeo...")

        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", self.audio_file,
            "-ar", "16000",
            "-ac", "1",
            output
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.audio_file = output

        print(f"✅ Áudio temporário criado: {output}")

    def _build_chunks_metadata(self):

        total_duration_ms = len(
            AudioSegment.from_file(self.audio_file)
        )

        chunk_ms = self.chunk_duration_seconds * 1000

        num_chunks = math.ceil(
            total_duration_ms / chunk_ms
        )

        chunks = []

        for i in range(num_chunks):

            chunks.append({
                "start": i * self.chunk_duration_seconds,
                "end": min(
                    (i + 1) * self.chunk_duration_seconds,
                    total_duration_ms / 1000
                )
            })

        print(f"🔊 Split lógico em {num_chunks} chunks")

        return chunks

    def _cut_segment(self, start_sec, end_sec):

        tmp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=True
        )

        subprocess.run([
            "ffmpeg",
            "-y",
            "-ss", str(start_sec),
            "-to", str(end_sec),
            "-i", self.audio_file,
            "-ar", "16000",
            "-ac", "1",
            tmp_file.name
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return AudioSegment.from_file(tmp_file.name)

    def split(self):
        return LazyAudioParts(self)

    @property
    def chunks(self):

        for i, parte in enumerate(self._chunks):

            yield {
                "index": i,
                "start": parte["start"],
                "end": parte["end"],
                "audio": self._cut_segment(
                    parte["start"],
                    parte["end"]
                )
            }