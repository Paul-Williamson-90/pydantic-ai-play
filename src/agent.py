import os
from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext, ModelMessage
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from .deps import Deps
from .tools import router_toolset, jobs_toolset, approvals_toolset

load_dotenv()


def create_model() -> OpenAIChatModel:
    return OpenAIChatModel(
        model_name="gpt-5.2",
        provider=OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")),
        settings=ModelSettings(
            max_tokens=1000,
        )
    )
    
    
def get_system_prompt() -> str:
    return (
        "You are a helpful assistant that provides information to users based on their requests. "
        "You can only help the user via tool calls and responding with information. "
        "All information must come from the tools you use and the context available to you. "
        "Do not invent information or tools."
    )


def context_processor(
    ctx: RunContext[Deps],
    messages: list[ModelMessage],
) -> list[ModelMessage]:
    if len(messages) >= ctx.deps.max_messages:
        messages = messages[-ctx.deps.reduce_messages_to:]
    return messages


def create_agent() -> Agent[Deps]:
    agent = Agent(
        model=create_model(),
        system_prompt=get_system_prompt(),
        deps_type=Deps,
        name="Agent",
        history_processors=[
            context_processor
        ],
        retries=5,
        toolsets=[
            router_toolset,
            jobs_toolset,
            approvals_toolset
        ],
    )
    return agent