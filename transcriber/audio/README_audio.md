# Módulo de Áudio

O módulo de áudio é a base do pipeline de transcrição do sistema. Ele foi projetado para processar arquivos de áudio e vídeo de forma eficiente, escalável e com baixo consumo de memória, permitindo trabalhar tanto com pequenos arquivos quanto com mídias longas sem comprometer a performance.

A arquitetura é dividida em dois componentes principais:

- **AudioSplitter** → responsável pela segmentação inteligente do áudio utilizando lazy loading.
- **AudioProcessor** → responsável pela orquestração da transcrição e montagem do resultado final.

Juntos, esses componentes formam um fluxo contínuo de processamento capaz de:

- extrair áudio de vídeos,
- dividir automaticamente em segmentos,
- reduzir uso de memória,
- integrar diferentes engines de reconhecimento de fala,
- gerar timestamps globais,
- consolidar transcrições finais.

---

#  Estrutura do Pipeline

O fluxo do módulo segue a seguinte arquitetura:

```text
Vídeo/Áudio
      ↓
AudioSplitter
(segmentação lazy)
      ↓
Chunks de áudio
      ↓
AudioProcessor
(orquestração)
      ↓
SpeechEngine
(Vosk / Whisper / etc.)
      ↓
Transcrição formatada
      ↓
Consolidação final
```

---

# 🚀 Objetivos do Módulo

O módulo foi desenvolvido para resolver problemas comuns em pipelines de transcrição:

- ❌ Alto consumo de RAM em arquivos longos
- ❌ Processamento monolítico de grandes mídias
- ❌ Dificuldade de integrar diferentes engines
- ❌ Ausência de timestamps globais
- ❌ Reprocessamento custoso

A solução adotada utiliza:

- segmentação em chunks
- lazy loading
- liberação manual de memória
- normalização de resultados
- processamento incremental

---

#  Principais Recursos

##  Compatibilidade com Áudio e Vídeo

O sistema suporta:

- `.wav`
- `.mp3`
- `.flac`
- `.ogg`
- `.mp4`
- `.mkv`
- `.avi`
- `.mov`

A extração de áudio é feita automaticamente via **ffmpeg**.

---

##  Lazy Loading

Os segmentos de áudio não permanecem carregados em memória.

Cada chunk é carregado apenas quando acessado:

```python
segmento = partes[0]
```

Após o uso, pode ser liberado:

```python
partes.release(0)
```

Isso permite processar arquivos extremamente longos mantendo baixo consumo de RAM.

---

##  Transcrição com Timestamp Global

O `AudioProcessor` converte automaticamente offsets em timestamps legíveis:

```text
[00:12:30] → trecho transcrito
```

Isso facilita:

- localização do trecho original,
- indexação,
- sincronização com legendas,
- pós-processamento.

---

##  Integração com Engines de Fala

O sistema foi desenhado para desacoplar a engine de reconhecimento do pipeline principal.

### Engines suportadas

- Vosk
- Whisper
- SpeechRecognition
- Engines customizadas

---

##  Gerenciamento de Memória

Durante o processamento:

- chunks podem ser descartados manualmente,
- `gc.collect()` é executado automaticamente,
- objetos temporários são liberados após uso.

Isso melhora estabilidade em:

- áudios longos,
- processamento em lote,
- ambientes com pouca RAM.

---

#  Diretrizes de Performance

Para melhor equilíbrio entre:

- precisão,
- velocidade,
- estabilidade,

recomenda-se:

| Duração do Chunk | Recomendação |
|---|---|
| 30 segundos | Ideal |
| Até 60 segundos | Máximo recomendado |
| Acima de 60 segundos | Não funcional |

Chunks menores geralmente produzem:

- melhor precisão,
- menor uso de memória,
- menor risco de falhas.

---

#  Componentes do Sistema

##  AudioSplitter

Responsável pela divisão inteligente do áudio.

### Recursos

- Lazy loading
- Conversão automática para WAV 16kHz mono
- Extração de áudio de vídeo
- Cache sob demanda
- Liberação manual de memória

---

##  AudioProcessor

Responsável pela orquestração da transcrição.

### Recursos

- Integração com SpeechEngine
- Timestamp global automático
- Normalização de saída
- Tratamento de erros
- Consolidação final dos blocos

---

#  Exemplo Completo de Pipeline

```python
import os

from transcriber.audio.audio_splitter import AudioSplitter
from transcriber.audio.audio_processor import AudioProcessor

# garante pasta de saída
os.makedirs("transcription_chunks", exist_ok=True)

DURACAO_SEG = 30

splitter = AudioSplitter(
    "meu_video.mp4",
    chunk_duration_seconds=DURACAO_SEG
)

partes = splitter.split()

processor = AudioProcessor(
    engine="vosk",
)

for i in range(len(partes)):
    segmento = partes[i]

    offset_ms = i * DURACAO_SEG * 1000

    idx, texto, duracao = processor.process_chunk(
        i,
        segmento,
        offset_ms,
        "pt-br"
    )

    caminho = f"transcription_chunks/bloco_{i:03d}.txt"

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f"💾 Salvo: {caminho}")

    # libera memória do chunk
    partes.release(i)

# monta transcrição final
transcricao_final = processor.build_final_transcription(
    pasta="transcription_chunks"
)

print(transcricao_final)
```

---

#  Dependências

## FFmpeg

Necessário para extração e conversão de áudio.

### Ubuntu/Debian

```bash
sudo apt install ffmpeg
```

### MacOS

```bash
brew install ffmpeg
```

### Windows

Baixe em:

- FFmpeg Official Website

---

## Dependências Python

```bash
pip install pydub
```

---

#  Casos de Uso

Este módulo é ideal para:

- sistemas de transcrição,
- legendagem automática,
- diarização,
- indexação de áudio,
- análise de reuniões,
- processamento de podcasts,
- pipelines de IA de voz.