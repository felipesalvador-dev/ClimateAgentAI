# PLANO-01 — Plano de Implementação: Chat CLI Strands + OpenAI

| Campo          | Valor                                              |
|----------------|----------------------------------------------------|
| ID             | PLANO-01                                           |
| Escopo         | RF-01 (funcional) + DD-01 (design técnico)         |
| Status         | Aprovado para execução                             |
| Data           | 2026-11-07                                         |

---

## 1. Objetivo

Entregar o agente de chat via CMD conforme **RF-01** e **DD-01**: Python local,
`strands-agents` + `OpenAIModel`, memória persistente em `.sessions/` via
`FileSessionManager`, tool `current_datetime` e configuração via `.env`.

## 2. Premissas

- Python >= 3.10 instalado na máquina do usuário.
- Usuário possui uma `OPENAI_API_KEY` válida (será inserida no `.env` por ele —
  o plano não envolve acesso à chave real).
- Conexão com internet para `pip install` e chamadas à API OpenAI.
- Execução e verificação feitas localmente (Windows, CMD/PowerShell/Git Bash).

## 3. Agentes de IA necessários

| Agente               | Perfil/função                                        | Responsabilidades                                                        |
|----------------------|------------------------------------------------------|--------------------------------------------------------------------------|
| **Agente Implementador** | Agente de codificação (Devin / `subagent_general`) | Criar e editar `main.py`, `tools.py`, `requirements.txt`, `.env.example`, `.gitignore` |
| **Agente QA**        | Agente executor com acesso a shell                     | Instalar dependências, rodar smoke tests, validar critérios de aceite CA-01 a CA-09 |
| **Agente Revisor**   | Agente somente leitura (`subagent_explore`)            | Comparar código entregue com DD-01; checar RN-01..RN-08 e anti-padrões     |
| **Tech Lead (orquestrador)** | Sessão principal do Devin                     | Sequenciar atividades, consolidar resultados, reportar ao usuário          |

> Observação: em projeto deste porte, Implementador e QA podem ser a mesma
> sessão do Devin; o Revisor roda como subagente separado para revisão
> independente (evita "o autor avaliar o próprio código").

## 4. Atividades

### Fase A — Preparação do ambiente

| ID    | Atividade                                                              | Agente         | Saída/entregável                        | Depende de |
|-------|------------------------------------------------------------------------|----------------|-----------------------------------------|------------|
| A-01  | Verificar versão do Python (`python --version` >= 3.10)                 | Agente QA      | Confirmação de pré-requisito            | —          |
| A-02  | Criar `requirements.txt` (`strands-agents[openai]`, `python-dotenv`)    | Implementador  | `requirements.txt`                      | —          |
| A-03  | Criar `.env.example` (OPENAI_API_KEY, OPENAI_MODEL, SESSION_ID)         | Implementador  | `.env.example`                          | —          |
| A-04  | Criar/atualizar `.gitignore` (`.env`, `.sessions/`, `__pycache__/`)     | Implementador  | `.gitignore`                            | —          |
| A-05  | Criar `.env` real a partir do `.env.example` (usuário informa a chave)  | **Usuário**    | `.env` com `OPENAI_API_KEY`             | A-03       |
| A-06  | `pip install -r requirements.txt` (venv opcional, recomendado)          | Agente QA      | Ambiente pronto                         | A-02       |

### Fase B — Implementação

| ID    | Atividade                                                              | Agente         | Saída/entregável   | Depende de |
|-------|------------------------------------------------------------------------|----------------|--------------------|------------|
| B-01  | Implementar `tools.py`: `current_datetime` com `@tool` (DD-01 §5.1)     | Implementador  | `tools.py`         | —          |
| B-02  | Implementar `main.py`: bootstrap (dotenv, validação da chave),          | Implementador  | `main.py`          | B-01       |
|       | `FileSessionManager` + `OpenAIModel` + `Agent`, loop do chat            |                |                    |            |
|       | (filtros de entrada, comando de saída, try/except, Ctrl+C — DD-01 §5.3) |                |                    |            |
| B-03  | Auto-revisão: lint mental + conformidade com RN-01..RN-08               | Implementador  | Código revisado    | B-02       |

### Fase C — Verificação (critérios de aceite)

| ID    | Atividade                                                              | Agente         | CA coberto  | Depende de |
|-------|------------------------------------------------------------------------|----------------|-------------|------------|
| C-01  | Rodar sem `OPENAI_API_KEY` → mensagem clara, exit != 0                  | Agente QA      | CA-05, RN-07| A-06, B-02 |
| C-02  | Rodar com `.env` válido → prompt `>` exibido; enviar "Olá" → resposta   | Agente QA      | CA-01, CA-02| C-01       |
| C-03  | Enviar pergunta dependente de contexto → resposta usa histórico         | Agente QA      | CA-03       | C-02       |
| C-04  | Perguntar "que dia é hoje?" / "que horas são?" → tool é invocada        | Agente QA      | CA-08, RN-08| C-02       |
| C-05  | Digitar `sair`/`exit`/`quit` → despedida, exit 0                        | Agente QA      | CA-04       | C-02       |
| C-06  | Enviar Enter em branco → sem chamada de API, loop intacto               | Agente QA      | CA-07, RN-06| C-02       |
| C-07  | Ctrl+C durante o loop → encerramento limpo                              | Agente QA      | FA-02       | C-02       |
| C-08  | Encerrar, rodar de novo, perguntar sobre a conversa anterior → retomada | Agente QA      | CA-09, RN-05| C-03       |
| C-09  | Simular chave inválida/sem rede → erro exibido, loop continua           | Agente QA      | CA-06, FA-01| C-02       |

### Fase D — Revisão e fechamento

| ID    | Atividade                                                              | Agente         | Depende de |
|-------|------------------------------------------------------------------------|----------------|------------|
| D-01  | Revisão independente: código × DD-01; checar segredos fora do código,   | Agente Revisor | C-01..C-09 |
|       | `.gitignore` cobrindo `.env` e `.sessions/`                              |                |            |
| D-02  | Corrigir apontamentos da revisão                                        | Implementador  | D-01       |
| D-03  | Fechamento: checklist final assinado, docs atualizadas (status no RF-01  | Tech Lead      | D-02       |
|       | passa de "Em refinamento" para "Implementado")                          |                |            |

## 5. Sequenciamento

```
A-01 ─┐
A-02 ─┼─> A-06 ────────────────────────────┐
A-03 ─┼─> A-05 (usuário)                    ├─> C-01..C-09 ─> D-01 ─> D-02 ─> D-03
A-04 ─┘                                     │
B-01 ─> B-02 ─> B-03 ───────────────────────┘
```

Ordem prática: Fase A e B-01 podem correr em paralelo; verificação só começa
com ambiente + código prontos e chave configurada.

## 6. Definition of Done

- [ ] `main.py`, `tools.py`, `requirements.txt`, `.env.example`, `.gitignore` criados conforme DD-01.
- [ ] Nenhuma chave hardcoded; `.env` e `.sessions/` fora do versionamento.
- [ ] CA-01 a CA-09 verificados com evidência (saída do terminal).
- [ ] Revisão independente (D-01) sem pendências críticas.
- [ ] RF-01 com status atualizado.

## 7. Riscos e mitigações

| Risco                                                        | Mitigação                                                        |
|--------------------------------------------------------------|------------------------------------------------------------------|
| Versão/assinatura do `FileSessionManager` mudar entre releases | QA valida C-08 cedo; fixar versão mínima no `requirements.txt`     |
| Chave inválida ou cota esgotada durante testes                | Erros tratados no loop (CA-06); teste C-09 cobre o cenário         |
| `.sessions/` corrompido em máquina Windows (permissão/lock)    | Documentar workaround: apagar `.sessions/` ou trocar `SESSION_ID`  |
| Encoding de terminal Windows (acentos no input)               | Garantir resposta em PT-BR; se necessário, `chcp 65001` / UTF-8    |

## 8. Acompanhamento

- **Checkpoint 1** (fim da Fase A): ambiente instalado, `.env` pronto.
- **Checkpoint 2** (fim da Fase B): código completo, auto-revisão feita.
- **Checkpoint 3** (fim da Fase C): evidências de cada CA registradas.
- **Checkpoint 4** (fim da Fase D): revisão aprovada → entrega.

Cada checkpoint reporta ao usuário: o que foi feito, evidências e pendências.
Em caso de bloqueio (ex.: chave ausente em A-05), o plano pausa no checkpoint
e notifica o usuário em vez de improvisar.
