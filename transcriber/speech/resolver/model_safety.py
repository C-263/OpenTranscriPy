import psutil

class ModelSafety:
    DANGEROUS_LEVELS = ["medium", "large", "large-v3"]
    SAFE_LEVELS = ["tiny", "base", "small"]

    # Mapeamento baseado na sua tabela de requisitos (RAM mínima recomendada por modelo)
    MODEL_RAM_REQUIREMENTS = {
        "vosk": 2.0,  # Vosk Small precisa de ~2GB
        "tiny": 4.0,  # Whisper Tiny precisa de ~4GB
        "base": 4.0,  # Whisper Base precisa de ~4GB
        "small": 8.0,  # Whisper Small precisa de ~8GB
        "medium": 16.0,  # Whisper Medium precisa de ~16GB
        "large": 16.0,  # Whisper Large precisa de ~16GB
        "large-v3": 16.0  # Faster Whisper Large-v3 precisa de ~16GB
    }

    @staticmethod
    def require_confirmation(engine: str, model_type: str) -> dict:
        model_type = model_type.lower()
        engine = engine.lower()

        # 1. Coleta a RAM real do sistema do usuário em GB
        total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)

        # 2. Define o requisito mínimo com base no modelo (ou usa 4GB como padrão caso não ache no mapa)
        required_ram = ModelSafety.MODEL_RAM_REQUIREMENTS.get(model_type, 4.0)
        if engine == "vosk":
            required_ram = ModelSafety.MODEL_RAM_REQUIREMENTS.get("vosk")

        # 3. Se o sistema do usuário NÃO atende os requisitos de hardware
        # (Usamos uma margem de 0.5GB pois o Sistema Operacional esconde um pedaço da RAM total)
        if total_ram_gb < (required_ram - 0.5):
            return {
                "allowed": False,
                "require_confirmation": True,
                "reason": (
                    f"⚠️ O modelo '{model_type}' ({engine}) exige no mínimo {int(required_ram)} GB de RAM.\n"
                    f"   Seu sistema possui atualmente apenas {total_ram_gb:.1f} GB de RAM disponíveis.\n"
                    f"   O processamento pode travar ou ficar extremamente lento."
                )
            }

        # 4. Caso o hardware seja bom, mas o modelo ainda pertença ao grupo pesado (Dangerous)
        # enviamos um aviso preventivo mais brando
        if model_type in ModelSafety.DANGEROUS_LEVELS:
            return {
                "allowed": True,
                "require_confirmation": True,
                "reason": (
                    f"🔔 Nota: O modelo '{model_type}' é classificado como pesado.\n"
                    f"   Seu sistema possui RAM compatível ({total_ram_gb:.1f} GB), "
                    f"mas este processo causará alto uso de CPU/GPU."
                )
            }

        # 5. Tudo seguro e verificado
        return {
            "allowed": True,
            "require_confirmation": False,
            "reason": "Hardware verificado e compatível com o modelo selecionado."
        }