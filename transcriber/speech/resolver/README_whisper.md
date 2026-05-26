# Resolver Whisper
Este módulo fornece uma camada de segurança e validação para carregar modelos do Whisper (`openai-whisper`). Ele garante que modelos que consomem muitos recursos não sejam carregados acidentalmente sem uma confirmação explícita.
---
## Configuração
O módulo utiliza dois dicionários de mapeamento para validar e classificar os modelos suportados:

```python
WHISPER_MODELS = {
    "tiny": "tiny",
    "base": "base",
    "small": "small",
    "medium": "medium",
    "large": "large",
    "large-v3": "large-v3",  # Faster Whisper
}
```

```python
# Requisito mínimo de RAM por modelo (em GB), usado pelo ModelSafety via psutil
MODEL_RAM_REQUIREMENTS = {
    "vosk":      2.0,
    "tiny":      4.0,
    "base":      4.0,
    "small":     8.0,
    "medium":   16.0,
    "large":    16.0,
    "large-v3": 16.0,
}
```
---
# ModelSafety Utility
O `ModelSafety` é um componente de segurança para o gerenciamento de permissões de execução de modelos de IA, projetado para prevenir o uso acidental de modelos que exigem alto consumo de recursos (CPU/RAM). Ele coleta em tempo real a RAM disponível no sistema via `psutil` antes de liberar ou bloquear qualquer modelo.
## Funcionalidade
A classe atua como um "guardião", validando o tipo de modelo antes da execução. Ela classifica os modelos em dois grupos:
- **Safe Levels (`tiny`, `base`, `small`):** Modelos leves considerados seguros para execução imediata.
- **Dangerous Levels (`medium`, `large`, `large-v3`):** Modelos pesados que exigem confirmação do usuário para evitar sobrecarga do sistema.
---
## Estrutura da Classe
### `ModelSafety`
| Método | Parâmetros | Retorno | Descrição |
|---|---|---|---|
| `require_confirmation` | `engine`, `model_type` | `dict` | Verifica se o modelo requer permissão extra. |
---
## Exemplo de Uso
```python
# Verificação de segurança
status = ModelSafety.require_confirmation("my_engine", "large")
if not status["allowed"]:
    print(status["reason"])
    if status["require_confirmation"]:
        confirm = input("Deseja continuar mesmo assim? (s/n): ")
        # Lógica de prosseguimento...
```
---
## Estrutura de Retorno
O método `require_confirmation` retorna um dicionário contendo:
- `allowed (bool)`: Indica se a execução é permitida sem restrições.
- `reason (str)`: Explicação com detalhes sobre a RAM do sistema e os requisitos do modelo.
- `require_confirmation (bool)`: Indica se o sistema deve solicitar uma interação do usuário.

O retorno pode assumir três estados distintos, dependendo da RAM detectada pelo `psutil` e do nível do modelo:

| Condição | `allowed` | `require_confirmation` |
|---|---|---|
| RAM do sistema abaixo do mínimo exigido | `False` | `True` |
| RAM suficiente, mas modelo é Dangerous | `True` | `True` |
| RAM suficiente e modelo é Safe | `True` | `False` |

> **Margem de 0.5 GB:** a checagem usa `total_ram_gb < (required_ram - 0.5)` para compensar a RAM consumida pelo Sistema Operacional, evitando bloqueios falsos em sistemas no limite.
---
# Função: `resolve_whisper_model`
Esta função centraliza a validação, a segurança e a resolução do modelo.
## Assinatura
```python
resolve_whisper_model(model_type: str, confirm: bool = False) -> str
```
---
## Comportamento
1. **Validação de Nome:**  
   Verifica se o `model_type` fornecido está no dicionário `WHISPER_MODELS`. Se não, levanta `ValueError`.
2. **Checagem de Segurança:**  
   Invoca o `ModelSafety` para verificar se o modelo é considerado "pesado".
3. **Controle de Fluxo:**
   - Se a RAM do sistema for insuficiente para o modelo, a função levanta `PermissionError` independentemente de `confirm`.
   - Se o modelo for considerado perigoso (`medium`, `large` ou `large-v3`) e `confirm` for `False`, a função levanta `PermissionError`.
   - Se o usuário passar `confirm=True`, a trava de modelo pesado é ignorada e o modelo é retornado.
---
## Exemplos de Implementação
### Uso Padrão (Bloqueio automático para modelos pesados)
```python
try:
    # Tentativa de carregar um modelo grande sem confirmação
    model = resolve_whisper_model("large")
except PermissionError as e:
    print(f"Bloqueado: {e}")
```
---
### Uso com Confirmação
```python
try:
    # Forçando o carregamento do modelo grande
    model = resolve_whisper_model("large", confirm=True)
    print(f"Modelo {model} carregado com sucesso.")
except PermissionError as e:
    print(f"Erro: {e}")
```
---
## Tratamento de Erros
| Exceção | Causa |
|---|---|
| `ValueError` | Nome do modelo não reconhecido pelo sistema |
| `PermissionError` | RAM do sistema insuficiente para o modelo solicitado |
| `PermissionError` | Modelo pesado solicitado sem a flag `confirm=True` |