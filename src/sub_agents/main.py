import asyncio

from pydantic_ai import Agent, ModelMessage

from .core import create_core_agent
from .deps import Deps


async def conversation_loop(agent: Agent, deps: Deps, chat_history: list[ModelMessage]):
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting conversation.")
            break
        response = await agent.run(
            user_prompt=user_input,
            message_history=chat_history,
            deps=deps,
        )
        chat_history = response.all_messages()
        last_message = chat_history[-1]
        print("Agent:", "\n".join([p.content for p in last_message.parts]))


def main():
    agent = create_core_agent()
    deps = Deps()
    chat_history: list[ModelMessage] = []
    asyncio.run(conversation_loop(agent, deps, chat_history))
    


if __name__ == "__main__":
    main()
