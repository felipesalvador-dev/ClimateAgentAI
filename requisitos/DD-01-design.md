# DD-01 — Design Técnico: Chat CLI com Strands Agents + OpenAI

| Campo          | Valor                                        |
|----------------|----------------------------------------------|
| ID             | DD-01                                        |
| Título         | Design técnico do agente de chat via CMD     |
| Requisito      | RF-01 — Chat interativo via CMD              |
| Status         | Em refinamento                               |
| Data           | 2026-11-07                                   |

---

## 1. Visão geral

Agente de chat de terminal em Python, construído sobre o SDK **Strands
Agents** (`strands-agents`), usando o provider `OpenAIModel` para chamadas à
API da OpenAI. O agente possui:

- Loop interativo stdin/stdout;
- **Memória persistente em arquivo local** via `FileSessionManager` (a
  conversa é retomada entre execuções);
- **Tool customizada** de data/hora para responder perguntas temporais;
- Configuração sensível (API key, modelo) via `.env` + `python-dotenv`.

## 2. Arquitetura

```mermaid
flowchart LR
    U[Usuário<br/>CMD] -->|stdin| M[main.py<br/>loop do chat]
    M -->|prompt| A[Agent<br/>strands.Agent]
    A -->|histórico| S[FileSessionManager<br/>.sessions/]
    A -->|mensagens| M
    A -->|chamada de tool| T[current_datetime<br/>@tool]
    T -->|str data/hora| A
    A -->|API HTTP| O[OpenAI API<br/>gpt-4o-mini]
    O -->|resposta| A
    A -->|stdout| U
    E[.env<br/>OPENAI_API_KEY] -.->|python-dotenv| M
```

### Responsabilidades por componente

| Componente          | Responsabilidade                                                                 |
|---------------------|----------------------------------------------------------------------------------|
| `main.py`           | Carregar `.env`, validar `OPENAI_API_KEY`, montar o `Agent`, rodar o loop do chat |
| `tools.py`          | Definir a tool `current_datetime` com o decorator `@tool`                          |
| `FileSessionManager`| Serializar mensagens/estado da sessão em JSON dentro de `.sessions/`              |
| `.env`              | `OPENAI_API_KEY` (obrigatória), `OPENAI_MODEL` e `SESSION_ID` (opcionais)          |

## 3. Stack e dependências

| Item            | Escolha                          | Justificativa                                      |
|-----------------|----------------------------------|----------------------------------------------------|
| Linguagem       | Python >= 3.10                   | Exigência do strands-agents; compatível com Windows |
| SDK de agente   | `strands-agents[openai]`         | SDK da AWS; extra `openai` traz o `OpenAIModel`    |
| LLM             | `gpt-4o-mini` (OpenAI)           | Custo baixo, suficiente para chat simples          |
| Config/secrets  | `python-dotenv` + `.env`         | Chave fora do código                               |
| Sessão/memória  | `FileSessionManager`             | Persistência nativa do SDK em arquivo JSON          |

`requirements.txt`:

```txt
strands-agents[openai]>=1.0.0
python-dotenv>=1.0.0
```

## 4. Configuração

`.env.example` (versionado; o `.env` real fica no `.gitignore`):

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini   # opcional — default no código
SESSION_ID=chat-local      # opcional — identifica a sessão persistida
```

Regras:

- `OPENAI_API_KEY` ausente → abortar com mensagem clara **antes** do loop (RN-07).
- `OPENAI_MODEL`/`SESSION_ID` ausentes → usar defaults (`gpt-4o-mini`, `chat-local`).

## 5. Design dos componentes

### 5.1 Tool `current_datetime`

```python
from datetime import datetime
from strands import tool

@tool
def current_datetime() -> str:
    """Retorna a data e hora atuais do sistema local."""
    return datetime.now().astimezone().isoformat(timespec="seconds")
```

- Tool **customizada** (não a built-in `strands_tools.current_time`), conforme
  decisão de design — didática e sem dependência extra de `strands-agents-tools`.
- Assinatura sem parâmetros; docstring é o que o modelo usa para decidir
  quando invocá-la.
- `astimezone()` garante o offset do fuso local na resposta.

### 5.1.1 Tool `current_temperature`

- Assinatura: `current_temperature(city: str = "") -> dict`, em `tools.py`.
- Fluxo: Open-Meteo Geocoding (`geocoding-api.open-meteo.com/v1/search`) →
  latitude/longitude → Open-Meteo Forecast (`api.open-meteo.com/v1/forecast`,
  `current=temperature_2m,apparent_temperature,relative_humidity_2m`).
- HTTP via `urllib` da biblioteca padrão (sem dependência nova), timeout 10s.
- `city` vazio → `DEFAULT_CITY` do `.env` (padrão `Sao Paulo`).
- Retorno: `cidade`, `temperatura_c`, `sensacao_termica_c`, `umidade_percent`,
  `horario_medicao`; em falha, `{"erro": ...}` para o modelo explicar ao usuário.

### 5.2 Agente (`strands.Agent`)

```python
session_manager = FileSessionManager(
    session_id=os.getenv("SESSION_ID", "chat-local"),
    storage_dir=".sessions",
)

model = OpenAIModel(model_id=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

agent = Agent(
    model=model,
    session_manager=session_manager,
    system_prompt="Você é um assistente útil. Responda em português.",
    tools=[current_datetime, current_temperature],
    callback_handler=None,
)
```

- `FileSessionManager` grava cada mensagem em `.sessions/` em JSON; ao
  reiniciar com o mesmo `session_id`, o `Agent` reidrata o histórico e a
  conversa **retoma de onde parou** (RF-01, RN-05 revisada).
- O `OpenAIModel` lê `OPENAI_API_KEY` do ambiente (carregada pelo dotenv).

### 5.3 Loop do chat (`main`)

```python
while True:
    try:
        user_input = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAté logo!")
        break

    if not user_input:
        continue
    if user_input.lower() in {"sair", "exit", "quit"}:
        print("Até logo!")
        break

    try:
        result = agent(user_input)
        print(result, "\n")
    except Exception as e:
        print(f"Erro ao chamar o agente: {e}\n")
```

- Erros de API (rede, chave inválida, rate limit) não derrubam o loop (FA-01).
- `KeyboardInterrupt`/`EOFError` encerram de forma limpa (FA-02).

## 6. Persistência da sessão

- Diretório `.sessions/` na raiz do projeto, criado automaticamente pelo
  `FileSessionManager`.
- Formato: JSON por mensagem/estado, gerenciado pelo SDK — o código da
  aplicação **não** manipula os arquivos diretamente.
- `.sessions/` deve estar no `.gitignore` (pode conter dados da conversa).
- Para começar uma conversa do zero: apagar `.sessions/` ou trocar o
  `SESSION_ID`.

## 7. Estrutura do projeto

```
projeto/
├── main.py            # bootstrap + loop do chat
├── tools.py           # current_datetime (@tool)
├── .env               # secrets (não versionado)
├── .env.example       # template
├── .gitignore         # .env, .sessions/, __pycache__/
├── requirements.txt
├── .sessions/         # gerado em runtime — sessões persistidas
└── requisitos/
    ├── RF-01-chat-cli-agent.md
    └── DD-01-design.md
```

## 8. Fluxo de execução (sequência)

1. `main()` → `load_dotenv()` → valida `OPENAI_API_KEY` (erro → exit 1).
2. Instancia `FileSessionManager(session_id, ".sessions")`.
3. Instancia `OpenAIModel(model_id)`.
4. Instancia `Agent(model, session_manager, tools, system_prompt)` — se
   `.sessions/<session_id>` existe, histórico é restaurado.
5. Loop: `input("> ")` → filtros (vazio/sair) → `agent(msg)` → `print`.
6. Tool calls acontecem transparentemente dentro de `agent()`: o modelo
   decide chamar `current_datetime`, o SDK executa e devolve o resultado ao
   modelo, que gera a resposta final.
7. Comando de saída ou Ctrl+C → mensagem de despedida → exit 0.

## 9. Tratamento de erros

| Falha                              | Comportamento                                          |
|------------------------------------|--------------------------------------------------------|
| `OPENAI_API_KEY` ausente/inválida  | Ausente: aborta no boot. Inválida: erro no loop, continua |
| Sem internet / timeout da API      | Mensagem de erro; loop continua                        |
| `.sessions/` corrompido            | Erro do SDK sobe como exceção no `agent()` → loop continua; workaround documentado: apagar `.sessions/` |
| Ctrl+C / Ctrl+D                    | Encerra com despedida, exit 0                          |

## 10. Rastreabilidade (RF-01 → Design)

| Regra (RF-01) | Atendido por                                     |
|---------------|--------------------------------------------------|
| RN-01 rodar local | `python main.py`                                |
| RN-02 Strands + OpenAI | `strands.Agent` + `OpenAIModel`           |
| RN-03 modelo configurável | `OPENAI_MODEL` no `.env`               |
| RN-04 chave não hardcoded | `.env` + `python-dotenv`               |
| RN-05 memória de sessão | `FileSessionManager` + `.sessions/` (persistente) |
| RN-06 ignorar vazio | `if not user_input: continue`                |
| RN-07 validar chave | checagem no bootstrap                        |
| FA-01 erro sem derrubar | try/except no `agent()`                    |
| FA-02 Ctrl+C limpo | `KeyboardInterrupt`/`EOFError`                  |

## 11. Decisões e alternativas consideradas

| Decisão                       | Alternativa rejeitada                          | Motivo da escolha                          |
|-------------------------------|------------------------------------------------|--------------------------------------------|
| `FileSessionManager`          | Histórico manual em JSON/JSONL                  | Nativo do SDK; retoma sessão sem código extra |
| Tool customizada `@tool`      | `strands_tools.current_time` (pacote de tools)  | Menos uma dependência; mais didático        |
| `gpt-4o-mini`                 | `gpt-4o` / `gpt-4.1`                            | Custo; suficiente para chat simples         |
| Dois arquivos (`main`, `tools`) | Arquivo único `main.py`                       | Separa tools da orquestração; fácil adicionar novas tools |
