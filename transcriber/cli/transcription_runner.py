import os
import json
from pathlib import Path
from transcriber.audio import AudioSplitter
from transcriber.speech.speech_engine import SpeechEngine
from transcriber.jobs.transcription_job import TranscriptionJob


class TranscriptionRunner:
    CACHE_DIR = Path(__file__).resolve().parents[2] / "cache_transcricao"

    def __init__(self, config: dict):
        self.engine_name: str = config["engine"]
        self.model_config: dict = config["model_config"]
        self.audio_path: str = config["audio_path"]
        self.block_duration: int = config["block_duration"]
        self.job_name: str = config["job_name"]
        self.with_words: bool = self.model_config.get("with_words", False)  # ← flag central

    def run(self) -> str | None:
        engine = self._build_engine()
        splitter, partes = self._split_audio()
        job = self._setup_job()
        if job is False:
            return None

        texto_final = self._restore_cache(job, partes)
        texto_final = self._process_blocks(job, partes, engine, texto_final)

        print("\n🧾 Formatando...\n")
        final_file = job.final_path
        print(f"✅ Final: {final_file}")
        print("\n🏁 FIM")
        return final_file


    def _build_engine(self) -> SpeechEngine:
        return SpeechEngine(
            engine_name=self.engine_name,
            model_config=self.model_config,
        )

    def _split_audio(self) -> tuple[AudioSplitter, list[dict]]:
        splitter = AudioSplitter(self.audio_path, self.block_duration)
        lazy = splitter.split()
        partes = [
            {
                "index": i,
                "start": splitter._chunks[i]["start"],
                "end": splitter._chunks[i]["end"],
                "audio": lazy[i],
            }
            for i in range(len(lazy))
        ]
        print(f"✅ {len(partes)} blocos")
        return splitter, partes

    def _setup_job(self) -> TranscriptionJob | bool:
        job = TranscriptionJob(
            cache_dir=self.CACHE_DIR,
            audio_path=self.audio_path,
            job_name=self.job_name,
        )
        status = job.select_job()
        if status is False:
            return False

        return job

    def _restore_cache(self, job: TranscriptionJob, partes: list[dict]) -> list:
        texto_final = []
        for i in range(len(partes)):
            if job.block_exists(i):
                texto_final.append(job.load_block(i))
            else:
                break
        return texto_final

    def _process_blocks(
            self,
            job: TranscriptionJob,
            partes: list[dict],
            engine: SpeechEngine,
            texto_final: list,
    ) -> list:
        idioma = self.model_config.get("lang", "pt-br")
        print("\n🧠 Processando...\n")

        for i, parte in enumerate(partes):
            if job.block_exists(i):
                print(f"⏩ Bloco {i} cache")
                bloco = job.load_block(i)
            else:
                import time
                import gc

                inicio_parte = time.perf_counter()

                offset_ms = parte["start"]
                timestamp = self._seconds_to_hms(offset_ms / 1000)

                raw = engine.transcribe(parte["audio"], idioma=idioma)

                if isinstance(raw, dict):
                    texto = raw.get("text", "").strip() or "[Erro: não reconhecido]"
                    bloco = {**raw, "text": f"[{timestamp}] {texto}"}
                else:
                    texto = (raw or "").strip() or "[Erro: não reconhecido]"
                    bloco = f"[{timestamp}] {texto}"

                duracao = time.perf_counter() - inicio_parte
                print(f"🎧 Bloco {i + 1} concluído em {duracao:.2f}s")

                del parte["audio"]
                gc.collect()

                job.save_block(i, self._serializar(bloco))

            texto_final.append(bloco)
            job.save_final([self._serializar(b) for b in texto_final])

        return texto_final

    @staticmethod
    def _seconds_to_hms(segundos: float) -> str:
        h = int(segundos // 3600)
        m = int((segundos % 3600) // 60)
        s = int(segundos % 60)
        return f"{h:02}:{m:02}:{s:02}"

    @staticmethod
    def _serializar(bloco) -> str:
        """Converte str ou dict (with_words) para string armazenável."""
        if isinstance(bloco, dict):
            return json.dumps(bloco, ensure_ascii=False)
        return bloco or ""

    @staticmethod
    def _deserializar(raw: str):
        """Tenta restaurar dict do cache; retorna str se não for JSON."""
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw