# CLI — Interface de Transcrição

Este módulo é o ponto de entrada do pipeline. Ele coleta os parâmetros do usuário via terminal (`TranscriptionInput`), constrói a configuração necessária e delega a execução ao orquestrador (`TranscriptionRunner`).

---

## Componentes

### TranscriptionInput

Responsável por guiar o usuário através de menus interativos no terminal, validar as entradas e montar o dicionário de configuração que será consumido pelo `TranscriptionRunner`.

**Fluxo do método `collect()`**

1. Seleção da engine (Vosk, SpeechRecognition, Whisper ou Faster Whisper)
2. Configuração do modelo (submenus específicos por engine)
3. Confirmação interativa para modelos pesados (`medium`, `large`, `large-v3`)
4. Seleção de idioma (Whisper/SpeechRecognition: lista fixa; Vosk: apenas idiomas com modelo baixado no disco)
5. Localização do arquivo de áudio (valida existência no sistema de arquivos)
6. Definição do tamanho dos blocos em segundos — **pulada automaticamente** se o áudio tiver ≤ 60s
7. Geração automática do `job_name` para evitar colisões de cache

**Engines disponíveis**

| Opção | Engine             | Detalhes                                                                    |
|-------|--------------------|-----------------------------------------------------------------------------|
| 1     | vosk               | Modelos small/base; suporte a `with_words`; idiomas filtrados por modelos presentes no disco |
| 2     | speech_recognition | Engine via Google Speech Recognition (apenas para testes)                   |
| 3     | whisper            | Modelos tiny a large; medium/large exigem confirmação interativa            |
| 4     | faster_whisper     | Modelos tiny a large-v3; medium/large-v3 exigem confirmação interativa; seleciona `compute_type` automaticamente por dispositivo |

**Seleção de idioma**

Os mappings de idioma ficam centralizados em `config.py` e são importados pela classe.

- Whisper, Faster Whisper e SpeechRecognition usam códigos ISO 639-1 (`pt`, `en`, `es`…) definidos em `WHISPER_LANG_MAP`.
- Vosk usa códigos no formato `ll-CC` (`pt-br`, `en-us`…) definidos em `VOSK_LANG_MAP`. O menu exibe **apenas os idiomas cujo diretório existe em `VOSK_PATH`** (definido em `path.py`). Se nenhum modelo estiver baixado, o pipeline é interrompido com `FileNotFoundError`.

```
Idioma (modelos disponíveis):
[1] Português (Brasil)
[2] English (US)
Escolha (default 1):
```

**Tamanho dos blocos**

Se o áudio tiver duração de **até 60 segundos**, a pergunta é pulada e o arquivo é processado em bloco único automaticamente.

```
⏱️  Duração: 30.00s
   → Áudio curto, processando em bloco único.
```

Para áudios mais longos, o usuário pode informar o tamanho do bloco manualmente (padrão: 60s).

**Confirmação de modelos pesados**

Os modelos `medium`, `large` e `large-v3` exigem confirmação explícita do usuário antes de serem carregados, independentemente da engine escolhida. Caso o usuário não confirme, o pipeline é interrompido com `ValueError`.

```
⚠️  'large-v3' é um modelo pesado e exige bastante RAM/VRAM.
   Engine: Faster Whisper
Confirmar mesmo assim? [s/N]:
```

**Saída do `collect()`**

Whisper, modelo leve:
```python
{
    "engine": "whisper",
    "model_config": {"model_type": "small", "lang": "pt", "confirm": False},
    "audio_path": "audios/aula.mp3",
    "block_duration": 60,
    "job_name": "whisper_small"
}
```

Faster Whisper, modelo pesado confirmado, GPU:
```python
{
    "engine": "faster_whisper",
    "model_config": {
        "model_type": "large-v3",
        "device": "cuda",
        "compute_type": "float16",
        "lang": "pt",
        "confirm": True
    },
    "audio_path": "audios/aula.mp3",
    "block_duration": 60,
    "job_name": "faster_whisper_large-v3"
}
```

Vosk, com palavras:
```python
{
    "engine": "vosk",
    "model_config": {"model_type": "small", "lang": "pt-br", "with_words": True},
    "audio_path": "audios/aula.mp3",
    "block_duration": 31,
    "job_name": "vosk_small_words"
}
```

**Dependências:** `pydub` (cálculo de duração do arquivo de áudio), `config.py` (mappings de idioma), `path.py` (localização dos modelos Vosk)

---

### TranscriptionRunner

Orquestrador central do pipeline. Recebe o dicionário de configuração produzido pelo `TranscriptionInput` e gerencia todo o fluxo: segmentação do áudio, verificação de cache, processamento por blocos e persistência dos resultados.

**Fluxo do método `run()`**

1. Inicializa a engine de fala com as configurações fornecidas
2. Segmenta o áudio via `AudioSplitter`
3. Define o diretório de cache e o identificador do job
4. Carrega blocos já processados (se existirem)
5. Processa apenas os blocos ausentes do cache
6. Persiste os resultados (texto simples ou JSON)

**Exemplo de configuração**

```python
from transcriber.cli.transcription_runner import TranscriptionRunner

config = {
    "engine": "faster_whisper",
    "model_config": {
        "model_type": "small",
        "device": "cpu",
        "compute_type": "int8",
        "lang": "pt",
        "confirm": False
    },
    "audio_path": "audios/aula.mp3",
    "block_duration": 60,
    "job_name": "faster_whisper_small"
}

runner = TranscriptionRunner(config)
resultado = runner.run()
```

**Cache**

Os resultados são salvos em `cache_transcricao/`, organizados por job e bloco. A serialização e desserialização de tipos (string ou JSON) é tratada internamente pelos métodos `_serializar` e `_deserializar`.

**Dependências internas**

- `transcriber.audio.audio_splitter.AudioSplitter`
- `transcriber.speech.speech_engine.SpeechEngine`
- `transcriber.jobs.transcription_job.TranscriptionJob`

---

## Como executar

```bash
python -m main
```

O menu interativo guiará você pelas opções. Abaixo dois exemplos de fluxo completo:

**Whisper — modelo leve, áudio curto**

```
🎧 PIPELINE DE TRANSCRIÇÃO

Engine:
[1] Vosk
[2] SpeechRecognition
[3] Whisper
[4] Faster Whisper
Escolha: 3

Modelo Whisper:
[1] tiny
[2] base
[3] small (recomendado)
[4] medium ⚠️
[5] large ⚠️
Escolha: 3

Idioma:
[1] Português
[2] English
...
Escolha (default 1 – Português):
   → Português (pt)

Fonte:
[1] Arquivo local
Escolha: 1
Arquivo: audios/aula.mp3

⏱️  Duração: 30.00s
   → Áudio curto, processando em bloco único.

📂 Jobs encontrados:
[1] whisper_small
[N] Novo job
Escolha: 1

[1] Continuar
[2] Resetar
Escolha: 1

🧠 Processando...
✅ Final: cache_transcricao/bloco_0/jobs/whisper_small/final.txt
🏁 FIM
```

**Faster Whisper — modelo pesado com confirmação, áudio longo**

```
🎧 PIPELINE DE TRANSCRIÇÃO

Engine:
[1] Vosk
[2] SpeechRecognition
[3] Whisper
[4] Faster Whisper
Escolha: 4

Modelo Faster Whisper:
[1] tiny
[2] base
[3] small (recomendado)
[4] medium ⚠️
[5] large-v3 ⚠️
Escolha: 5

⚠️ O modelo 'large-v3' (faster whisper) exige no mínimo 16 GB de RAM.
   Seu sistema possui atualmente apenas 9.6 GB de RAM disponíveis.
   O processamento pode travar ou ficar extremamente lento.
   Engine: Faster Whisper
Confirmar execução mesmo assim? [s/N]: s

Dispositivo:
[1] cpu
[2] cuda (GPU)
Escolha: 2

Idioma:
[1] Português
[2] English
...
Escolha (default 1 – Português):
   → Português (pt)

Fonte:
[1] Arquivo local
Escolha: 1
Arquivo: audios/aula.mp3

⏱️  Duração: 3600.00s
Bloco em segundos (default 60):

🔄 Carregando Faster-Whisper: large-v3
🧠 Processando...
✅ Final: cache_transcricao/bloco_0/jobs/faster_whisper_large-v3/final.txt
🏁 FIM
```

---

## Sistema de jobs

Cada execução é identificada pelo padrão `<engine>_<modelo>` (ex: `whisper_small`, `faster_whisper_large-v3`). Jobs são isolados por engine e modelo — não é possível reutilizar o histórico de uma engine em outra.

| Situação                         | Comportamento                               |
|----------------------------------|---------------------------------------------|
| Job inexistente                  | Cria novo job e processa todos os blocos    |
| Job compatível (mesma engine)    | Oferece opção de continuar ou resetar       |
| Job incompatível (outra engine)  | Bloqueado automaticamente com mensagem de erro |

**Exemplos de `job_name` gerados automaticamente**

| Engine         | Modelo    | `job_name`                  |
|----------------|-----------|-----------------------------|
| whisper        | small     | `whisper_small`             |
| whisper        | large     | `whisper_large`             |
| faster_whisper | small     | `faster_whisper_small`      |
| faster_whisper | large-v3  | `faster_whisper_large-v3`   |
| vosk           | small     | `vosk_small`                |
| vosk + words   | small     | `vosk_small_words`          |

---

## Tratamento de erros

| Exceção              | Causa                                                        |
|----------------------|--------------------------------------------------------------|
| `ValueError`         | Engine inválida, configuração incompatível ou modelo pesado não confirmado pelo usuário |
| `FileNotFoundError`  | Caminho do arquivo de áudio inexistente, ou nenhum modelo Vosk baixado em `VOSK_PATH` |
| `PermissionError`    | Modelo pesado carregado sem `confirm=True` no `model_config` |
| `JobMismatchError`   | Tentativa de usar job pertencente a outra engine             |

---

## Arquivos de suporte

| Arquivo     | Responsabilidade                                                                 |
|-------------|----------------------------------------------------------------------------------|
| `config.py` | `WHISPER_LANG_MAP` (ISO 639-1) e `VOSK_LANG_MAP` (ll-CC) — fonte única dos mappings de idioma |
| `path.py`   | `VOSK_PATH` — localização dos modelos Vosk no disco; usado para filtrar o menu de idiomas |

---

## Recomendações de performance

- Use blocos de **30s a 60s** por chunk para melhor equilíbrio entre precisão e uso de memória.
- **Vosk** é recomendado para execução leve e offline.
- **Whisper small** oferece boa precisão com uso moderado de recursos.
- **Faster Whisper** é significativamente mais rápido que o Whisper padrão para o mesmo modelo; prefira-o quando o tempo de processamento for crítico.
- **medium/large/large-v3** requerem GPU ou CPU robusta; o sistema solicita confirmação interativa antes de carregar esses modelos.
- Em GPU, o `compute_type` é definido automaticamente como `float16`; em CPU, `int8`.

> **Nota sobre CUDA:** ao selecionar `cuda`, o Faster Whisper tentará usar a GPU. Se nenhuma GPU compatível estiver disponível no momento da execução, a biblioteca recairá automaticamente para CPU — o pipeline não será interrompido, apenas rodará mais lento.