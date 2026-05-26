import os
from pydub import AudioSegment

from transcriber.speech.resolver import ModelSafety
from transcriber.config.config_language import WHISPER_LANG_MAP, VOSK_LANG_MAP
from transcriber.config.paths import VOSK_PATH


class TranscriptionInput:
    ENGINE_MAP = {
        "1": "vosk",
        "2": "speech_recognition",
        "3": "whisper",
        "4": "faster_whisper",
    }

    WHISPER_MODEL_MAP = {
        "1": "tiny",
        "2": "base",
        "3": "small",
        "4": "medium",
        "5": "large",
    }

    HEAVY_MODELS = {"medium", "large", "large-v3"}

    def collect(self) -> dict:
        print("🎧 PIPELINE DE TRANSCRIÇÃO\n")
        engine = self._ask_engine()
        model_config = self._ask_model_config(engine)
        audio_path = self._ask_audio_path()
        block_duration = self._ask_block_duration(audio_path)

        job_name = engine
        if "model_type" in model_config:
            job_name += f"_{model_config['model_type']}"
        if model_config.get("with_words"):
            job_name += "_words"

        return {
            "engine": engine,
            "model_config": model_config,
            "audio_path": audio_path,
            "block_duration": block_duration,
            "job_name": job_name,
        }

    def _ask_engine(self) -> str:
        print("Engine:")
        print("[1] Vosk")
        print("[2] SpeechRecognition")
        print("[3] Whisper")
        print("[4] Faster Whisper")
        choice = input("Escolha: ").strip()
        engine = self.ENGINE_MAP.get(choice)
        if not engine:
            raise ValueError(f"❌ Engine inválida: '{choice}'")
        return engine

    def _ask_model_config(self, engine: str) -> dict:
        if engine == "vosk":
            return self._ask_vosk_config()
        if engine == "whisper":
            return self._ask_whisper_config()
        if engine == "faster_whisper":
            return self._ask_faster_whisper_config()
        # speech_recognition: só pergunta idioma
        lang = self._ask_language_whisper()
        return {"lang": lang}

    def _confirm_heavy_model(self, engine_label: str, model_type: str) -> bool:
        safety_check = ModelSafety.require_confirmation(engine_label, model_type)

        # Se exigir confirmação (seja por falta de RAM ou por ser um modelo perigoso)
        if safety_check["require_confirmation"]:
            print(f"\n{safety_check['reason']}")
            print(f"   Engine: {engine_label}")

            resp = input("Confirmar execução mesmo assim? [s/N]: ").strip().lower()
            if resp != "s":
                raise ValueError(
                    f"❌ Operação cancelada pelo usuário para o modelo '{model_type}'."
                )

        return True

    # ------------------------------------------------------------------
    # Seleção de idioma
    # ------------------------------------------------------------------

    def _ask_language_whisper(self) -> str:
        """Retorna código ISO 639-1 para Whisper / Faster Whisper / SpeechRecognition."""
        print("\nIdioma:")
        for key, (code, label) in WHISPER_LANG_MAP.items():
            print(f"[{key}] {label}")
        choice = input("Escolha (default 1 – Português): ").strip() or "1"
        code, label = WHISPER_LANG_MAP.get(choice, ("pt", "Português"))
        print(f"   → {label} ({code})")
        return code

    def _ask_language_vosk(self) -> str:
        """Retorna código de idioma para Vosk (ex: 'pt-br').

        Exibe apenas os idiomas cujo diretório existe em VOSK_PATH.
        """
        disponiveis = {
            key: (code, label)
            for key, (code, label) in VOSK_LANG_MAP.items()
            if (VOSK_PATH / code).exists()
        }

        if not disponiveis:
            raise FileNotFoundError(
                f"❌ Nenhum modelo Vosk encontrado em '{VOSK_PATH}'. "
                "Baixe ao menos um modelo antes de continuar."
            )

        # Renumera as chaves para o menu ficar sempre sequencial (1, 2, 3…)
        menu = {str(i): v for i, v in enumerate(disponiveis.values(), start=1)}

        print("\nIdioma (modelos disponíveis):")
        for key, (code, label) in menu.items():
            print(f"[{key}] {label}")

        default_key = "1"
        choice = input(f"Escolha (default {default_key}): ").strip() or default_key
        code, label = menu.get(choice, next(iter(menu.values())))
        print(f"   → {label} ({code})")
        return code

    # ------------------------------------------------------------------
    # Configuração por engine
    # ------------------------------------------------------------------

    def _ask_whisper_config(self) -> dict:
        print("\nModelo Whisper:")
        print("[1] tiny")
        print("[2] base")
        print("[3] small (recomendado)")
        print("[4] medium ⚠️")
        print("[5] large ⚠️")
        m = input("Escolha: ").strip()
        model_type = self.WHISPER_MODEL_MAP.get(m, "small")

        confirm = False
        if model_type in self.HEAVY_MODELS:
            confirm = self._confirm_heavy_model("Whisper", model_type)

        lang = self._ask_language_whisper()
        return {"model_type": model_type, "lang": lang, "confirm": confirm}

    def _ask_faster_whisper_config(self) -> dict:
        print("\nModelo Faster Whisper:")
        print("[1] tiny")
        print("[2] base")
        print("[3] small (recomendado)")
        print("[4] medium ⚠️")
        print("[5] large-v3 ⚠️")
        m = input("Escolha: ").strip()
        model_map = {
            "1": "tiny", "2": "base", "3": "small",
            "4": "medium", "5": "large-v3",
        }
        model_type = model_map.get(m, "small")

        confirm = False
        if model_type in self.HEAVY_MODELS:
            confirm = self._confirm_heavy_model("Faster Whisper", model_type)

        print("\nDispositivo:")
        print("[1] cpu")
        print("[2] cuda (GPU)")
        dev = input("Escolha: ").strip()
        device = "cuda" if dev == "2" else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        lang = self._ask_language_whisper()
        return {
            "model_type": model_type,
            "device": device,
            "compute_type": compute_type,
            "lang": lang,
            "confirm": confirm,
        }

    def _ask_vosk_config(self) -> dict:
        print("\nModelo Vosk:")
        print("[1] small (seguro)")
        m = input("Escolha: ").strip()
        print("\nModo Vosk:")
        print("[1] Transcrição simples")
        print("[2] Transcrição com palavras (with_words)")
        modo = input("Escolha: ").strip()

        lang = self._ask_language_vosk()
        return {
            "lang": lang,
            "model_type": "small" if m == "1" else "base",
            "with_words": modo == "2",
        }

    def _ask_audio_path(self) -> str:
        print("\nFonte:")
        print("[1] Arquivo local")
        fonte = input("Escolha: ").strip()
        if fonte != "1":
            raise ValueError("❌ Apenas arquivo local é suportado nesta versão.")
        audio_path = input("Arquivo: ").strip()
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"❌ Arquivo não encontrado: '{audio_path}'")
        return audio_path

    def _ask_block_duration(self, audio_path: str) -> int:
        audio_seg = AudioSegment.from_file(audio_path)
        audio_seconds = len(audio_seg) / 1000
        print(f"\n⏱️  Duração: {audio_seconds:.2f}s")

        if audio_seconds <= 60:
            print("   → Áudio curto, processando em bloco único.")
            return int(audio_seconds) + 1  # margem para não cortar no limite exato

        raw = input("Bloco em segundos (default 60): ").strip()
        return int(raw) if raw else 60