# TranscriptionJob

O `TranscriptionJob` é o módulo responsável pelo gerenciamento de jobs de transcrição e persistência em cache dos resultados processados.

Ele organiza automaticamente a estrutura de diretórios do projeto, permitindo:

- Separação de múltiplos jobs por áudio
- Continuação de transcrições interrompidas
- Reset de jobs específicos
- Cache por blocos de transcrição
- Persistência do resultado final

O objetivo principal é evitar reprocessamentos desnecessários durante pipelines longos de transcrição.

---

# Estrutura de Diretórios

Ao iniciar um job, o sistema cria automaticamente a seguinte estrutura:

```txt
cache/
└── nome_do_audio/
    └── jobs/
        ├── whisper_pt/
        │   ├── bloco_0.txt
        │   ├── bloco_1.txt
        │   └── final.txt
        │
        └── vosk_pt/
            ├── bloco_0.txt
            ├── bloco_1.txt
            └── final.txt
```

---

# Funcionalidades

## Gerenciamento de Jobs

Cada engine/modelo pode possuir seu próprio job independente.

Isso permite:

- Comparar resultados entre engines
- Continuar execuções antigas
- Manter múltiplas versões da transcrição
- Evitar sobrescrita de resultados

---

## Sistema de Cache por Blocos

Cada segmento de áudio processado é salvo individualmente:

```txt
bloco_0.txt
bloco_1.txt
bloco_2.txt
```

Dessa forma:

- Blocos já processados não precisam ser executados novamente
- Interrupções podem ser retomadas
- O pipeline se torna resiliente a falhas

---

## Persistência do Resultado Final

Após o processamento completo, o sistema consolida todos os blocos em:

```txt
final.txt
```

---

# Proteção de Prefixos Reservados

O módulo possui proteção contra uso indevido de jobs reservados para engines específicas.

Prefixos protegidos:

```python
RESERVED_PREFIXES = [
    "whisper",
    "vosk",
    "speech_recognition"
]
```

Isso impede, por exemplo:

```txt
whisper_large
vosk_ptbr
speech_recognition_en
```

de serem reutilizados incorretamente por outro modelo.

---

# Fluxo de Operação

O fluxo básico funciona assim:

1. Usuário seleciona/cria um job
2. Sistema verifica blocos existentes
3. Blocos já processados são reutilizados
4. Novos blocos são transcritos
5. Resultado final é consolidado

---

# Exemplo de Uso

```python
from transcriber.jobs.transcription_job import TranscriptionJob

job = TranscriptionJob(
    cache_dir="./cache",
    audio_path="audio.mp3",
    job_name="whisper_pt"
)

# Seleciona ou cria job
job.select_job()

# Verifica cache
if not job.block_exists(0):
    texto = "Transcrição do bloco"

    job.save_block(0, texto)

# Carrega bloco salvo
conteudo = job.load_block(0)

print(conteudo)

# Salva resultado final
job.save_final([
    "Linha 1",
    "Linha 2"
])
```

---

# Métodos Principais

## `listar_jobs()`

Lista todos os jobs disponíveis do projeto atual.

---

## `alterar_job(job_name)`

Altera o job ativo.

---

## `escolher_job()`

Interface interativa para:

- Selecionar jobs existentes
- Criar novos jobs
- Resetar jobs antigos

---

## `bloco_existe(index)`

Verifica se um bloco já foi processado.

---

## `salvar_bloco(index, texto)`

Salva a transcrição de um bloco.

---

## `carregar_bloco(index)`

Carrega um bloco salvo anteriormente.

---

## `salvar_final(textos)`

Consolida e salva a transcrição final.

---

# Vantagens da Arquitetura

## Reprocessamento Inteligente

Evita execução redundante de blocos já transcritos.

---

## Escalabilidade

Permite trabalhar com:

- Áudios longos
- Múltiplos modelos
- Diferentes idiomas

---

## Recuperação de Falhas

Caso a aplicação seja interrompida:

- O progresso já salvo é preservado
- O processamento pode continuar do ponto anterior

---

## Organização Modular

Cada áudio possui:

- Seu próprio projeto
- Múltiplos jobs independentes
- Cache isolado

---

# Integração com o Pipeline

O `TranscriptionJob` normalmente é utilizado pelo orquestrador principal (`TranscriptionRunner`) durante o pipeline de transcrição:

```txt
AudioSplitter
    ↓
SpeechEngine
    ↓
TranscriptionJob
    ↓
final.txt
```

---

# Observações

O módulo foi projetado para funcionar com diferentes engines de reconhecimento de fala, incluindo:

- Whisper
- Vosk
- SpeechRecognition
- Engines customizadas

A arquitetura também facilita futura integração com:

- Banco de dados
- Transcrição distribuída
- Filas assíncronas
- Processamento paralelo
- Timestamps por palavra
- Versionamento de resultados