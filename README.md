# Chat CLI com AWS Strands + OpenAI

Agente de chat simples que roda no terminal do Windows (CMD), feito em Python com o
SDK **AWS Strands Agents** e um modelo da **OpenAI** (`gpt-4o-mini`).

O que ele faz:

- Conversa em português pelo terminal;
- **Lembra da conversa**, inclusive depois de fechar e abrir de novo (memória em arquivo local);
- Informa a **data e hora atuais**;
- Informa a **temperatura atual** de qualquer cidade (padrão: São Paulo), via Open-Meteo.

> Projeto desenvolvido com a ajuda do **Devin** (agente de IA da Cognition): do
> refinamento do requisito ao design, plano, implementação, testes de segurança e
> este README.

---

## Passo a passo

### 1. Pré-requisitos

- **Python 3.10 ou superior** (aqui foi usado o 3.14);
- Uma **chave da API da OpenAI** com créditos:
  https://platform.openai.com/api-keys
- Internet.

Para conferir o Python, abra o CMD e digite:

```
py --version
```

> **Use sempre `py`, e não `python`.** Neste computador, o comando `python` abre a
> Microsoft Store (erro *"Python was not found"*). O `py` é o launcher oficial
> do Python no Windows e acha a instalação certa.

### 2. Entrar na pasta do projeto

```
cd C:\Users\Teste\Desktop\projeto
```

### 3. Instalar as dependências (só na primeira vez)

```
py -m pip install -r requirements.txt
```

### 4. Configurar a chave no arquivo `.env`

Se o arquivo `.env` não existir, copie o modelo:

```
copy .env.example .env
```

Abra o `.env` e preencha:

```env
OPENAI_API_KEY=sk-proj-sua-chave-aqui   # obrigatória
OPENAI_MODEL=gpt-4o-mini                # opcional
SESSION_ID=chat-local                   # opcional - nome da conversa salva
DEFAULT_CITY=Sao Paulo                  # opcional - cidade padrão da temperatura
```

> Nunca compartilhe o `.env` nem cole a chave em chats, e-mails ou repositórios.

### 5. Rodar o chat

```
py main.py
```

Vai aparecer:

```
Chat iniciado. Digite 'sair' para encerrar.
>
```

### 6. Usar

```
> Ola, meu nome e Teste.
> Qual e o meu nome?
> Que dia e hoje e que horas sao?
> Qual e a temperatura?
> E em Recife?
```

**Para sair:** digite `sair`, `exit` ou `quit`, ou aperte `Ctrl+C`.

---

## Memória da conversa

- A conversa é salva automaticamente na pasta `.sessions/`;
- Ao rodar `py main.py` de novo, o agente **continua de onde parou**;
- **Para começar do zero:** apague a pasta `.sessions/` ou troque o `SESSION_ID`
  no `.env` (ex.: `SESSION_ID=conversa-2`).

> A conversa fica salva em texto puro. Não escreva senhas ou dados sensíveis no chat.

---

## Problemas comuns

| Mensagem | Causa | Solução |
|----------|-------|---------|
| `Python was not found` | O comando `python` aponta para a Microsoft Store | Use `py main.py` |
| `Erro: OPENAI_API_KEY nao configurada` | `.env` ausente ou chave não preenchida | Faça o passo 4 |
| `Error code: 401 - Incorrect API key` | Chave errada ou revogada | Gere uma nova chave e atualize o `.env` |
| `OpenAI threw rate limit error` (várias vezes) e depois `429 - You have no credits remaining` | Conta da OpenAI sem créditos | Adicione créditos em https://platform.openai.com/settings/organization/billing/ |
| `ModuleNotFoundError: No module named 'strands'` | Dependências não instaladas | Faça o passo 3 |
| `Erro ao inicializar o agente` | Pasta `.sessions/` corrompida | Apague a pasta `.sessions/` |
| "Cidade não encontrada" | Nome da cidade não reconhecido | Tente o nome completo, ex.: "Belo Horizonte" |

---

## Estrutura do projeto

```
projeto/
├── main.py              # inicia o chat: lê o .env, monta o agente e roda o loop
├── tools.py             # ferramentas do agente: data/hora e temperatura
├── requirements.txt     # dependências (strands-agents[openai], python-dotenv)
├── .env                 # sua chave e configurações (NÃO compartilhar)
├── .env.example         # modelo do .env
├── .gitignore           # impede versionar .env e .sessions/
├── .sessions/           # conversas salvas (criada automaticamente)
├── requisitos/
│   ├── RF-01-chat-cli-agent.md     # requisito funcional
│   ├── DD-01-design.md             # design técnico
│   └── PLANO-01-implementacao.md   # plano de implementação
└── seguranca/
    ├── RELATORIO-SEGURANCA-01.md   # testes adversariais (OWASP Agentic Top 10)
    ├── redteam.py                  # script dos testes de segurança
    └── results.json                # respostas completas dos testes
```

## Como funciona (resumo)

1. `main.py` carrega o `.env` e valida a chave;
2. Cria o agente Strands com o modelo da OpenAI, as duas ferramentas e a memória em
   arquivo (`FileSessionManager`);
3. A cada mensagem, o modelo decide se precisa chamar uma ferramenta (data/hora ou
   temperatura), recebe o resultado e responde;
4. Cada mensagem é gravada em `.sessions/`.

---

## Testes de segurança

Para rodar de novo os 15 testes adversariais (custo de centavos na OpenAI):

```
py seguranca\redteam.py
```

Os resultados e recomendações estão em `seguranca/RELATORIO-SEGURANCA-01.md`.
Pendências principais:

- [ ] **Revogar as chaves que foram coladas em chat** e gerar uma nova, com limite de gasto mensal;
- [ ] Reforçar o system prompt (F3);
- [ ] Limitar tokens, chamadas de ferramenta e retentativas (F4);
- [ ] Validar o nome da cidade (F5).

---

## Histórico do projeto

| Etapa | Entregável |
|-------|-----------|
| 1. Requisito | `requisitos/RF-01-chat-cli-agent.md` |
| 2. Design | `requisitos/DD-01-design.md` |
| 3. Plano | `requisitos/PLANO-01-implementacao.md` |
| 4. Implementação | `main.py`, `tools.py`, configuração |
| 5. Nova ferramenta | Temperatura via Open-Meteo |
| 6. Segurança | `seguranca/RELATORIO-SEGURANCA-01.md` |

Feito por **Teste**, com a ajuda do **Devin** (Cognition), em novembro de 2026.
