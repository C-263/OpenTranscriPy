# Speech Engines

Este diretório contém as implementações concretas das engines de reconhecimento de fala do projeto. Todas herdam de `BaseSpeechEngine` e expõem a interface comum `transcribe(audio_segment, idioma)`.

---

## Estrutura

```txt
engines/
├── base.py                          ← Contrato abstrato (ABC)
├── vosk_engine.py                   ← Engine offline (Vosk)
├── whisper_engine.py                ← Engine local via openai-whisper
├── faster_whisper_engine.py         ← Engine local via faster-whisper (CTranslate2)
└── speech_recognition_google_engine.py  ← Engine online via Google (apenas testes)
```

---

## Contrato Base (`base.py`)

Todas as engines implementam `BaseSpeechEngine`:

```python
class BaseSpeechEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_segment, idioma): ...
```

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `audio_segment` | `AudioSegment` | Áudio processado via `pydub` |
| `idioma` | `str` | Código do idioma (ex: `"pt-br"`, `"en"`) |

---

## Engines Disponíveis

### `VoskEngine`

Engine de transcrição **offline** baseada no Vosk. Ideal para ambientes sem acesso à internet.

**Destaques:**
- Cache de modelos em memória (`_models_cache`) para evitar recarregamentos.
- Suporte a múltiplos idiomas e tipos de modelo (`small`, `base`) via `vosk_resolver`.
- Método adicional `transcribe_with_words` que retorna timestamps por palavra.

**Inicialização:**

```python
engine = VoskEngine(model_config={"size": "small"})
```

**Transcrição simples:**

```python
text = engine.transcribe(audio_segment, idioma="pt-br")
```

**Transcrição com palavras:**

```python
result = engine.transcribe_with_words(audio_segment, idioma="pt-br")
# result = {"text": "...", "words": [...]}
```

---

### `WhisperEngine`

Engine de transcrição **local** baseada no modelo `openai-whisper`. Converte o `AudioSegment` para `numpy float32` antes da inferência.

**Destaques:**
- Integração com `ModelSafety` para bloquear modelos pesados (`medium`, `large`) sem confirmação explícita.
- Libera memória GPU automaticamente após cada transcrição (`torch.cuda.empty_cache()`).

**Inicialização:**

```python
# Modelo leve (sem confirmação necessária)
engine = WhisperEngine(model_config={"model_type": "small"})

# Modelo pesado (requer confirm=True)
engine = WhisperEngine(model_config={"model_type": "large", "confirm": True})
```

**Transcrição:**

```python
text = engine.transcribe(audio_segment, idioma="pt-br")
```

---

### `FasterWhisperEngine`

Engine de transcrição **local** baseada no `faster-whisper` (CTranslate2). Mais eficiente que a `WhisperEngine` padrão, com suporte nativo a CUDA.

**Destaques:**
- Detecta CUDA automaticamente via `torch` e ajusta `device` e `compute_type`.
- Mesma trava de segurança do `ModelSafety` aplicada no `__init__`.
- Parâmetro `beam_size` configurável (padrão: `5`).

**Inicialização:**

```python
engine = FasterWhisperEngine(model_config={
    "model_type": "small",
    "beam_size": 5,
})
```

**Transcrição:**

```python
text = engine.transcribe(audio_segment, idioma="pt-br")
```

---

### `SpeechRecognitionGoogleEngine`

Engine baseada na API do Google via `speech_recognition`. **Apenas para testes** — não permitida para distribuição.

**Destaques:**
- Requer conexão com a internet.
- Não possui trava de segurança nem resolução de modelo local.

**Inicialização:**

```python
engine = SpeechRecognitionGoogleEngine()
```

**Transcrição:**

```python
text = engine.transcribe(audio_segment, idioma="pt-br")
```

---

## Tabela Comparativa

| Engine | Modo | GPU | Confirmação para modelos pesados | Uso recomendado |
|---|---|---|---|---|
| `VoskEngine` | Offline | ✗ | ✗ | Produção offline, múltiplos idiomas |
| `WhisperEngine` | Local | ✓ | ✓ | Transcrições de alta qualidade |
| `FasterWhisperEngine` | Local | ✓ | ✓ | Melhor performance com CUDA |
| `SpeechRecognitionGoogleEngine` | Online | ✗ | ✗ | Testes rápidos apenas |

---

## Segurança de Modelos

As engines `WhisperEngine` e `FasterWhisperEngine` utilizam o `ModelSafety` para prevenir o carregamento acidental de modelos pesados. Ao tentar usar `medium` ou `large` sem `confirm=True`, uma `PermissionError` é levantada.

```python
# Bloqueado automaticamente
engine = WhisperEngine(model_config={"model_type": "large"})
# PermissionError: ...

# Permitido explicitamente
engine = WhisperEngine(model_config={"model_type": "large", "confirm": True})
```

> Para detalhes sobre o `ModelSafety` e os resolvers de modelo, consulte `README_whisper.md` e `README_vosk.md`.
