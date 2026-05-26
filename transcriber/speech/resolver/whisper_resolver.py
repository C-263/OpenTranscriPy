from .model_safety import ModelSafety

WHISPER_MODELS = {
    "tiny": "tiny",
    "base": "base",
    "small": "small",
    "medium": "medium",
    "large": "large",
}


def resolve_whisper_model(model_type: str, confirm: bool = False):

    model_type = model_type.lower()

    if model_type not in WHISPER_MODELS:
        raise ValueError(f"❌ Modelo Whisper inválido: {model_type}")

    safety = ModelSafety.require_confirmation("whisper", model_type)

    if safety["require_confirmation"] and not confirm:
        raise PermissionError(
            f"{safety['reason']} | Passe confirm=True para continuar"
        )

    return WHISPER_MODELS[model_type]