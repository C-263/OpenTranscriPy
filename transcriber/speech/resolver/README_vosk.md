# Configuração de Modelos Vosk

Este módulo gerencia o mapeamento e a resolução de diretórios dos modelos de reconhecimento de fala do Vosk utilizados no projeto.

---

## Estrutura de Configuração (`vosk_video_models.py`)

O dicionário `VIDEO_MODELS` atua como um "mapa" de busca. Ele define quais palavras-chave (`keywords`) o resolvedor deve procurar nos nomes das pastas dentro do diretório de modelos.

### Como funciona

- **Idiomas:** As chaves principais (ex: `pt-br`, `en`, `es`) definem o idioma.
- **Tipos de Modelo:** Dentro de cada idioma, definimos `small` e `base`.
- **Keywords:** A lista de strings em cada tipo indica os termos que obrigatoriamente devem estar presentes no nome da pasta para que ela seja considerada um candidato válido.

> **Nota:** Adicione novas entradas aqui caso baixe novas versões ou idiomas do Vosk. Certifique-se de que a estrutura das pastas no seu disco contenha as palavras-chave definidas.

---

## Estrutura de Pastas Esperada

Para que o resolvedor funcione corretamente, os modelos devem estar organizados da seguinte forma:

```txt
models/
└── vosk/
    ├── pt-br/
    │   └── vosk-model-small-pt-0.3/     ← keywords: ["small", "pt"]
    ├── en/
    │   └── vosk-model-small-en-us-0.15/ ← keywords: ["small"]
    └── es/
        └── vosk-model-small-es-0.42/    ← keywords: ["small"]
```

O caminho raiz `models/vosk/` é resolvido automaticamente via `VOSK_PATH` em `transcriber/config/paths.py`.

---

# Resolvedor de Modelos (`vosk_resolver.py`)

A função `resolve_vosk_model` é responsável por localizar o caminho correto do modelo em tempo de execução.

## Fluxo de Resolução

1. **Validação:** Verifica se o idioma e o `model_type` existem no arquivo de configuração.
2. **Busca:** Itera sobre as pastas no diretório do idioma (`base_path/lang`).
3. **Filtragem:** Compara se todas as `keywords` configuradas estão contidas no nome da pasta.
4. **Seleção:**
   - Caso encontre múltiplos candidatos (ex: `vosk-model-small-pt-0.22` e `vosk-model-small-pt-0.15`), o resolvedor aplica `sort(reverse=True)`.
   - **Prioridade:** A versão com o nome "maior" (geralmente a mais recente) é selecionada automaticamente.

---

## Exemplo de Uso

```python
from transcriber.speech.resolver.vosk_resolver import resolve_vosk_model
from transcriber.config.paths import VOSK_PATH

model_path = resolve_vosk_model(
    lang="pt-br",
    model_type="small",
    base_path=str(VOSK_PATH)  # caminho resolvido automaticamente via paths.py
)

print(f"Modelo selecionado: {model_path}")
```

---

## Tratamento de Erros

| Exceção | Causa |
|---|---|
| `ValueError` | Idioma ou `model_type` não configurado em `VOSK_MODELS` |
| `FileNotFoundError` | Diretório do idioma não encontrado, ou nenhuma pasta bate com as `keywords` |
