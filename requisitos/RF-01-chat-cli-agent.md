# RF-01 — Chat interativo via CMD com Strands Agents + OpenAI

| Campo          | Valor                                  |
|----------------|----------------------------------------|
| ID             | RF-01                                  |
| Título         | Chat interativo via linha de comando   |
| Tipo           | Requisito Funcional                    |
| Prioridade     | Alta                                   |
| Status         | Implementado — aguardando validação com chave real (CA-02, CA-03, CA-08, CA-09) |
| Autor          | Teste                                  |
| Data           | 2026-11-07                             |

---

## 1. Objetivo

Disponibilizar um agente de chat **super simples**, executado localmente via
terminal (CMD/PowerShell), que receba mensagens do usuário e responda usando um
modelo da OpenAI, orquestrado pelo SDK **Strands Agents** (AWS).

## 2. Descrição

O usuário executa um script Python no terminal. O programa inicia um loop de
conversa: o usuário digita uma mensagem, o agente processa via modelo da OpenAI
e imprime a resposta no terminal. O ciclo se repete até o usuário solicitar a
saída. O agente deve manter o histórico da conversa em memória durante a sessão.

## 3. Escopo

### Em escopo

- Interface de chat somente texto, via terminal (stdin/stdout).
- Loop interativo: ler entrada → chamar agente → exibir resposta.
- Memória de sessão **persistente em arquivo local**: a conversa é gravada em
  disco e retomada entre execuções (`FileSessionManager` do Strands).
- Comando(s) de saída: `sair`, `exit` ou `quit` (case-insensitive) encerram o
  programa de forma limpa.
- Carregamento da chave da OpenAI a partir de arquivo `.env` na raiz do projeto
  (`OPENAI_API_KEY`), usando `python-dotenv`.
- Uma tool customizada de **data/hora atual** (`@tool`), para que o agente
  responda corretamente perguntas temporais.
- Uma tool customizada de **temperatura atual** (`@tool`), via API Open-Meteo
  (gratuita, sem chave), para qualquer cidade informada na pergunta; sem cidade,
  usa `DEFAULT_CITY` do `.env` (padrão: São Paulo).

### Fora de escopo

- Interface gráfica (GUI) ou web.
- Persistência em banco de dados ou nuvem (a memória é apenas arquivo local).
- Tools adicionais além de data/hora e temperatura (ex.: previsão para outros dias), RAG, acesso a arquivos.
- Streaming de resposta token a token (pode ser v1.1 futura).
- Suporte a múltiplos usuários ou execução em servidor.
- Deploy, conteinerização ou CI/CD.

## 4. Atores

- **Usuário**: pessoa executando o script localmente no terminal.

## 5. Pré-condições

- Python 3.10+ instalado localmente.
- Dependências instaladas (`pip install -r requirements.txt`):
  - `strands-agents[openai]`
  - `python-dotenv`
- Arquivo `.env` presente na raiz com `OPENAI_API_KEY=<chave válida>`.
- Acesso à internet para chamadas à API da OpenAI.

## 6. Regras de negócio

| ID    | Regra                                                                                  |
|-------|----------------------------------------------------------------------------------------|
| RN-01 | A execução deve ser local: `python main.py` (ou equivalente) a partir do terminal.       |
| RN-02 | O agente deve usar o SDK `strands-agents` com o provider OpenAI (`OpenAIModel`).          |
| RN-03 | Modelo padrão: `gpt-4o-mini` (configurável via constante/variável no código).            |
| RN-04 | A chave da OpenAI nunca deve ser hardcoded; deve vir exclusivamente do `.env`.            |
| RN-05 | O histórico deve ser persistido em arquivo local e retomado na próxima execução (`FileSessionManager`, dir `.sessions/`). |
| RN-06 | Entrada vazia (somente espaços/Enter) deve ser ignorada, sem chamar a API.               |
| RN-07 | Falta da `OPENAI_API_KEY` deve abortar com mensagem clara de erro, antes do loop.         |
| RN-08 | O agente deve ter uma tool `current_datetime` que retorna a data/hora local, invocada automaticamente quando relevante. |
| RN-09 | O agente deve ter uma tool `current_temperature(city)` que retorna temperatura, sensação térmica e umidade atuais via Open-Meteo; cidade vazia usa `DEFAULT_CITY`. Falhas de rede/cidade inexistente retornam erro tratado, sem derrubar o chat. |

## 7. Fluxo principal

1. Usuário executa `python main.py`.
2. Sistema carrega o `.env` e valida a presença de `OPENAI_API_KEY`.
   - Se ausente → exibe erro orientando a configuração e encerra (código != 0).
3. Sistema instancia o `Agent` (Strands) com `OpenAIModel` e exibe prompt de boas-vindas.
4. Sistema exibe prompt `>` e aguarda entrada do usuário.
5. Se a entrada for `sair`/`exit`/`quit` → exibe despedida e encerra (código 0).
6. Se a entrada for vazia → volta ao passo 4.
7. Sistema envia a mensagem ao agente e imprime a resposta.
8. Retorna ao passo 4.

### Fluxos alternativos / exceção

- **FA-01 — Erro de API** (rede, chave inválida, rate limit): exibir mensagem de
  erro amigável e retornar ao prompt, sem encerrar o programa.
- **FA-02 — Ctrl+C/Ctrl+D**: capturar `KeyboardInterrupt`/`EOFError` e encerrar
  de forma limpa com mensagem de despedida.

## 8. Critérios de aceite

| ID    | Critério                                                                                                  |
|-------|-----------------------------------------------------------------------------------------------------------|
| CA-01 | Dado o `.env` configurado, ao rodar `python main.py` o chat inicia e exibe o prompt `>`.                     |
| CA-02 | Ao enviar "Olá", o agente responde em linguagem natural no próprio terminal.                                 |
| CA-03 | Ao perguntar algo que dependa de contexto anterior (ex.: "qual foi minha primeira pergunta?"), o agente responde corretamente usando o histórico da sessão. |
| CA-04 | Ao digitar `sair`, `exit` ou `quit` (qualquer caixa), o programa encerra sem erro.                           |
| CA-05 | Sem `OPENAI_API_KEY` no `.env`/ambiente, o programa aborta com mensagem clara e não chama a API.             |
| CA-06 | Com erro de rede ou chave inválida, o programa exibe o erro e continua aceitando novas mensagens.            |
| CA-07 | Entrada vazia não gera chamada à API nem quebra o loop.                                                      |
| CA-08 | Ao perguntar "que dia é hoje?" ou "que horas são?", o agente responde com a data/hora real (via tool).       |
| CA-09 | Ao encerrar e rodar o programa novamente, o agente retoma a conversa anterior (histórico persistido).      |
| CA-10 | Ao perguntar "qual é a temperatura?", responde com a temperatura atual da cidade padrão; ao perguntar "e em Recife?", responde para Recife. |

## 9. Estrutura sugerida do projeto

```
projeto/
├── main.py            # loop do chat + instanciação do Agent
├── tools.py           # tool current_datetime (@tool)
├── .env               # OPENAI_API_KEY=...  (não versionado)
├── .env.example       # template da variável necessária
├── requirements.txt   # strands-agents[openai], python-dotenv
├── .sessions/         # gerado em runtime — memória persistida (não versionado)
└── requisitos/
    ├── RF-01-chat-cli-agent.md
    └── DD-01-design.md
```

## 10. Referências

- Strands Agents SDK: https://strandsagents.com/
- OpenAI API: https://platform.openai.com/docs
