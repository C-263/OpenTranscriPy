# OpenTranscriPy

Pipeline modular de transcrição offline de áudio e vídeo com suporte a múltiplas engines de reconhecimento de fala, lazy loading, cache por blocos e interface de linha de comando interativa.

---

## Índice

- [Visão Geral](#visão-geral)
- [Instalação](#instalação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Módulos](#módulos)
  - [Audio](#audio)
  - [CLI](#cli)
  - [Speech / Engines](#speech--engines)
  - [Jobs](#jobs)
  - [Resolvers](#resolvers)
- [Como Executar](#como-executar)
- [Formatos Suportados](#formatos-suportados)

---

## Visão Geral

```text
Vídeo/Áudio
      ↓
AudioSplitter       — segmentação lazy em chunks
      ↓
AudioProcessor      — orquestração e timestamps globais
      ↓
SpeechEngine        — Vosk / Whisper / Google
      ↓
TranscriptionJob    — cache por bloco e persistência
      ↓
final.txt
```

## Requisitos do Sistema

### Requisitos mínimos por modelo

| Modelo | RAM mínima | Recomendado | Observações |
|---|---|---|---|
| Vosk Small | 2 GB | 4 GB | Melhor opção para PCs fracos |
| Whisper / Faster Whisper Tiny | 4 GB | 6 GB | Qualidade básica |
| Whisper / Faster Whisper Base | 4 GB | 8 GB | Bom equilíbrio |
| Whisper / Faster Whisper Small | 8 GB | 12 GB | Melhor precisão |
| Whisper / Faster Whisper Medium | 16 GB | 24 GB | Processamento pesado |
| Whisper / Faster Whisper Large | 16 GB | 32 GB | Alto consumo de memória |

### Observações

- O `Vosk Small` é a engine mais leve do projeto e a mais indicada para máquinas com pouca memória RAM.
- Modelos maiores podem utilizar muita memória RAM durante a transcrição.
- O Faster Whisper é mais otimizado e normalmente mais rápido que o Whisper tradicional.
- Em GPUs compatíveis, o Faster Whisper pode reduzir o consumo de memória e acelerar significativamente a transcrição.
- Em máquinas com pouca RAM, prefira:
  - `vosk`
  - `whisper tiny`
  - `whisper base`
  - `faster-whisper`
- O projeto utiliza segmentação lazy e cache por blocos para reduzir uso de memória.
---

## Instalação

### Dependências do Sistema

**FFmpeg** — necessário para extração e conversão de áudio.

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows — baixe em https://ffmpeg.org/download.html
```

### Dependências Python

```bash
pip install pydub

pip install psutil
```

**Engine Vosk:**
```bash
pip install vosk
```
Modelos disponíveis em: https://alphacephei.com/vosk/models

**Engine Whisper:**
```bash
pip install openai-whisper
```
Repositório: https://github.com/openai/whisper

**Engine Faster Whisper:**
```bash
pip install faster-whisper
```
Repositório: https://github.com/SYSTRAN/faster-whisper

**Engine Google (apenas testes):**
```bash
pip install SpeechRecognition
```
Repositório: https://github.com/Uberi/speech_recognition

---

## Estrutura do Projeto

```txt
pythonProjectTranscriPy/
│
├── main.py
├── README.md
│
├── transcriber/
│   ├── __init__.py
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── README_audio.md
│   │   ├── audio_processor.py
│   │   ├── audio_splitter.py
│   │   └── lazy_audio_parts.py
│   │
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── README_cli.md
│   │   ├── transcription_input.py
│   │   └── transcription_runner.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── paths.py
│   │
│   ├── speech/
│   │   ├── __init__.py
│   │   ├── README_speech.md
│   │   ├── speech_engine.py
│   │   ├── engines/
│   │   │   ├── __init__.py
│   │   │   ├── README_engines.md
│   │   │   ├── base.py
│   │   │   ├── vosk_engine.py
│   │   │   ├── whisper_engine.py
│   │   │   └── speech_recognition_google_engine.py
│   │   └── resolver/
│   │       ├── __init__.py
│   │       ├── README_vosk.md
│   │       ├── README_whisper.md
│   │       ├── vosk_video_models.py
│   │       ├── vosk_resolver.py
│   │       ├── whisper_resolver.py
│   │       └── model_safety.py
│   │
│   └── jobs/
│       ├── __init__.py
│       ├── README_job.md
│       └── transcription_job.py
│
├── models/
│   └── vosk/
│       └── pt-br/
│           └── vosk-model-small-pt-0.3/
│
└── cache_transcricao/
    └── audio_exemplo/
        └── jobs/
            ├── speech_recognition/
            ├── vosk_small/
            ├── whisper_small/
            └── audio_4_test/
```

---

## Módulos

### Audio

📄 **[`transcriber/audio/README_audio.md`](./transcriber/audio/README_audio.md)**

Responsável pela segmentação e orquestração do pipeline de áudio.

| Componente | Arquivo | Responsabilidade |
|---|---|---|
| `AudioSplitter` | `audio_splitter.py` | Divide o áudio em chunks com lazy loading |
| `LazyAudioParts` | `lazy_audio_parts.py` | Gerencia acesso e liberação de chunks em memória |
| `AudioProcessor` | `audio_processor.py` | Orquestra a transcrição e gera timestamps globais |

Principais características: lazy loading, extração automática de áudio de vídeo, liberação manual de memória (`partes.release(i)`), timestamps no formato `[HH:MM:SS]`.

---

### CLI

📄 **[`transcriber/cli/README_cli.md`](./transcriber/cli/README_cli.md)**

Ponto de entrada do pipeline via terminal.

| Componente | Arquivo | Responsabilidade |
|---|---|---|
| `TranscriptionInput` | `transcription_input.py` | Coleta parâmetros do usuário via menus interativos |
| `TranscriptionRunner` | `transcription_runner.py` | Orquestra o pipeline completo com base na configuração |

Execute com:

```bash
python main.py
```

---

### Speech / Engines

📄 **[`transcriber/speech/README_speech.md`](./transcriber/speech/README_speech.md)**

Camada de abstração e implementações concretas das engines de reconhecimento de fala. Todas herdam de `BaseSpeechEngine` e expõem `transcribe(audio_segment, idioma)`.

| Engine | Arquivo                               | Modo | GPU | Confirmação para modelos pesados |
|---|---------------------------------------|---|---|---|
| `VoskEngine` | `vosk_engine.py`                      | Offline | ✗ | ✗ |
| `WhisperEngine` | `whisper_engine.py`                   | Local | ✓ | ✓ |
| `FasterWhisperEngine` | `faster_whisper_engine.py`            | Local | ✓ | ✓ |
| `SpeechRecognitionGoogleEngine` | `speech_recognition_google_engine.py` | Online | ✗ | ✗ — apenas testes |

O `speech_engine.py` atua como orquestrador, instanciando a engine correta a partir da configuração recebida.

#### Ranking de Modelos

Ordem recomendada de uso, do melhor custo-benefício ao menos indicado:

| # | Modelo | Observação |
|---|---|---|
| 1 | Faster Whisper Small | Mais otimizado que o Whisper equivalente |
| 2 | Whisper Small | |
| 3 | speech_recognition | |
| 4 | Vosk Small | |
| 5 | Faster Whisper Base | Mais otimizado que o Whisper equivalente |
| 6 | Whisper Base | |
| 7 | Faster Whisper Tiny | Mais otimizado que o Whisper equivalente |
| 8 | Whisper Tiny | |

---

### Jobs

📄 **[`transcriber/jobs/README_job.md`](./transcriber/jobs/README_job.md)**

Gerenciamento de jobs e persistência de cache por bloco.

| Funcionalidade | Descrição |
|---|---|
| Cache por bloco | Cada chunk transcrito é salvo individualmente em `bloco_N.txt` |
| Retomada de pipeline | Blocos já processados não são reexecutados |
| Múltiplos jobs | Cada engine/modelo tem seu job independente |
| Proteção de prefixos | Jobs reservados por engine não podem ser reutilizados por outra |

Estrutura de cache gerada automaticamente em `cache_transcricao/`:

```txt
cache_transcricao/
└── nome_do_audio/
    └── jobs/
        ├── vosk_small/
        │   ├── bloco_0.txt
        │   └── final.txt
        └── whisper_small/
            ├── bloco_0.txt
            └── final.txt
```

---

### Resolvers

📄 **[`transcriber/speech/resolver/README_vosk.md`](./transcriber/speech/resolver/README_vosk.md)**
📄 **[`transcriber/speech/resolver/README_whisper.md`](./transcriber/speech/resolver/README_whisper.md)**

Camada de validação, segurança e resolução de caminhos de modelos.

| Componente | Arquivo | Descrição |
|---|---|---|
| `vosk_resolver` | `vosk_resolver.py` | Localiza o modelo Vosk correto por idioma e tipo, filtrando por keywords |
| `vosk_video_models` | `vosk_video_models.py` | Mapa de idiomas, tipos e keywords dos modelos Vosk |
| `whisper_resolver` | `whisper_resolver.py` | Valida o tipo de modelo Whisper e aplica a trava de segurança |
| `ModelSafety` | `model_safety.py` | Bloqueia modelos `medium` e `large` sem `confirm=True` |

---

## Como Executar

```bash
python main.py
```

Ou via código:

```python
from transcriber.cli.transcription_runner import TranscriptionRunner

config = {
    "engine": "vosk",
    "model_config": {"size": "small"},
    "audio_path": "audio.mp3",
    "block_duration": 30,
    "job_name": "vosk_small"
}

runner = TranscriptionRunner(config)
resultado = runner.run()
```

---

## Formatos Suportados

| Tipo | Extensões |
|---|---|
| Áudio | `.wav` `.mp3` `.flac` `.ogg` |
| Vídeo | `.mp4` `.mkv` `.avi` `.mov` |