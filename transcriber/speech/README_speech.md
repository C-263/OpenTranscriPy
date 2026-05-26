# SpeechEngine

`SpeechEngine` é a fachada central do módulo de fala. Ela abstrai a escolha e a inicialização da engine concreta, expondo uma interface única de transcrição para o restante do pipeline.

---

## Localização

```txt
transcriber/speech/speech_engine.py
```

---

## Responsabilidade

Em vez de o pipeline precisar conhecer cada engine individualmente, ele apenas instancia `SpeechEngine` com um nome e uma configuração. A fachada cuida de:

- Instanciar a engine correta via `_load_engine`.
- Resolver o idioma e o tipo de modelo a partir do `model_config`.
- Despachar a chamada de transcrição com os parâmetros certos para cada engine — incluindo `with_words` para o Vosk e `model_type` como argumento posicional onde necessário.

---

## Inicialização

```python
from transcriber.speech.speech_engine import SpeechEngine

engine = SpeechEngine(
    engine_name="vosk",
    model_config={"size": "small", "idioma": "pt-br"}
)
```

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `engine_name` | `str` | `"vosk"` | Identificador da engine a ser carregada |
| `model_config` | `dict` | `{}` | Configurações repassadas à engine concreta |

---

## Engines Suportadas

| `engine_name` | Classe instanciada | Observação |
|---|---|---|
| `"vosk"` | `VoskEngine` | Engine offline; aceita `size`, `idioma`, `with_words` |
| `"whisper"` | `WhisperEngine` | Engine local; aceita `model_type`, `confirm` |
| `"faster_whisper"` | `FasterWhisperEngine` | Engine local otimizada; aceita `model_type`, `confirm`, `beam_size` |
| `"speech_recognition"` | `SpeechRecognitionGoogleEngine` | Online; apenas testes — ignora `model_config` |

Qualquer outro valor levanta `ValueError`.

---

## Transcrição

```python
texto = engine.transcribe(audio_segment, idioma="pt-br")
```

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `audio_segment` | `AudioSegment` | — | Chunk de áudio processado via `pydub` |
| `idioma` | `str` | `None` | Código do idioma. Se omitido, usa `model_config["idioma"]` ou `"pt-br"` |

### Idioma padrão

O idioma é resolvido nesta ordem de prioridade:

```
argumento idioma → model_config["idioma"] → "pt-br"
```

---

## Comportamento de Despacho

O método `transcribe` adapta a chamada internamente dependendo da engine ativa:

**Vosk com `with_words=True`:**

```python
engine = SpeechEngine("vosk", {"size": "small", "with_words": True})
resultado = engine.transcribe(audio_segment)
# retorna {"text": "...", "words": [...]}
```

Quando `with_words=True` e a engine for `VoskEngine`, a fachada chama `transcribe_with_words` automaticamente, retornando o dicionário com texto e timestamps por palavra.

**Vosk padrão, Whisper, Faster Whisper e Google:**

```python
engine = SpeechEngine("whisper", {"model_type": "small"})
texto = engine.transcribe(audio_segment, idioma="en")
# retorna str
```

Retorna sempre uma `str` com o texto transcrito.

---

## Exemplos de Configuração

**Vosk — transcrição simples:**

```python
SpeechEngine("vosk", {
    "size": "small",
    "idioma": "pt-br"
})
```

**Vosk — com timestamps por palavra:**

```python
SpeechEngine("vosk", {
    "size": "small",
    "idioma": "pt-br",
    "with_words": True
})
```

**Whisper — modelo leve:**

```python
SpeechEngine("whisper", {
    "model_type": "small"
})
```

**Whisper — modelo pesado com confirmação:**

```python
SpeechEngine("whisper", {
    "model_type": "large",
    "confirm": True
})
```

**Faster Whisper — com beam_size customizado:**

```python
SpeechEngine("faster_whisper", {
    "model_type": "small",
    "beam_size": 3
})
```

**Google Speech Recognition (testes):**

```python
SpeechEngine("speech_recognition")
```

---

## Tratamento de Erros

| Exceção | Causa |
|---|---|
| `ValueError` | `engine_name` não reconhecido |
| `PermissionError` | Modelo pesado (`medium` / `large`) carregado sem `confirm=True` |
| `FileNotFoundError` | Modelo Vosk não encontrado no caminho resolvido |

---

## Relação com os Demais Componentes

```txt
TranscriptionRunner
      ↓
  SpeechEngine          ← fachada (este módulo)
      ↓
  _load_engine()
      ↓
VoskEngine / WhisperEngine / FasterWhisperEngine / SpeechRecognitionGoogleEngine
      ↓
  vosk_resolver / whisper_resolver / ModelSafety
```

> Para detalhes sobre cada engine concreta, consulte [`engines/README_engines.md`](./engines/README_engines.md).  
> Para detalhes sobre os resolvers e o `ModelSafety`, consulte [`resolver/README_vosk.md`](./resolver/README_vosk.md) e [`resolver/README_whisper.md`](./resolver/README_whisper.md).