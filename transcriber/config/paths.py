from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_PATH = BASE_DIR / "models"
VOSK_PATH = MODELS_PATH / "vosk"