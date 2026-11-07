import os
import sys

from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.session.file_session_manager import FileSessionManager

from tools import current_datetime, current_temperature

EXIT_COMMANDS = {"sair", "exit", "quit"}


def build_agent() -> Agent:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "sk-sua-chave-aqui":
        print(
            "Erro: OPENAI_API_KEY nao configurada.\n"
            "Crie um arquivo .env na raiz do projeto com OPENAI_API_KEY=<sua chave>."
        )
        sys.exit(1)

    session_manager = FileSessionManager(
        session_id=os.getenv("SESSION_ID", "chat-local"),
        storage_dir=".sessions",
    )

    model = OpenAIModel(model_id=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    return Agent(
        model=model,
        session_manager=session_manager,
        system_prompt="Voce e um assistente util. Responda em portugues.",
        tools=[current_datetime, current_temperature],
        callback_handler=None,
    )


def main() -> None:
    load_dotenv()
    try:
        agent = build_agent()
    except Exception as e:
        print(
            f"Erro ao inicializar o agente: {e}\n"
            "Se o diretorio .sessions/ estiver corrompido, apague-o para comecar uma nova sessao."
        )
        sys.exit(1)

    print("Chat iniciado. Digite 'sair' para encerrar.")
    while True:
        try:
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAte logo!")
            break

        if not user_input:
            continue
        if user_input.lower() in EXIT_COMMANDS:
            print("Ate logo!")
            break

        try:
            result = agent(user_input)
            print(f"{result}\n")
        except KeyboardInterrupt:
            print("\nAte logo!")
            break
        except Exception as e:
            print(f"Erro ao chamar o agente: {e}\n")


if __name__ == "__main__":
    main()
