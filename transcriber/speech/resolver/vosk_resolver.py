import os
from transcriber.speech.resolver.vosk_video_models import VIDEO_MODELS

def resolve_vosk_model(lang: str, model_type: str, base_path: str):

    lang = lang.lower()
    model_type = model_type.lower()

    if lang not in VIDEO_MODELS:
        raise ValueError(f"❌ Idioma não suportado: {lang}")

    lang_dir = os.path.join(base_path, lang)

    if not os.path.exists(lang_dir):
        raise FileNotFoundError(f"❌ Idioma não encontrado: {lang_dir}")

    keywords = VIDEO_MODELS[lang].get(model_type)

    if not keywords:
        raise ValueError(f"❌ model_type inválido: {model_type}")

    candidatos = []

    for folder in os.listdir(lang_dir):
        folder_lower = folder.lower()

        # match mais robusto
        if all(k in folder_lower for k in keywords):
            candidatos.append(folder)

    if not candidatos:
        raise FileNotFoundError(
            f"❌ Nenhum modelo encontrado para {lang}/{model_type}"
        )

    candidatos.sort(reverse=True)

    chosen = candidatos[0]

    return os.path.join(lang_dir, chosen)