import os
from typing import cast
from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext, ModelMessage
from pydantic_ai.models import ModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel

from .deps import Deps
from .tools import (
    create_router_toolset,
    create_approvals_toolset,
    create_jobs_toolset,
)
from .enums import AgentModes

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


def create_core_agent() -> Agent[Deps]:
    agent = Agent(
        model=create_model(),
        instructions=get_system_prompt(),
        deps_type=Deps,
        name="Core Agent",
        history_processors=[
            context_processor
        ],
        retries=5,
        toolsets=[
            create_router_toolset(max_retries=5),
            create_jobs_toolset(max_retries=5).filtered(
                filter_func=lambda ctx, _: cast(Deps, ctx.deps).agent_mode == AgentModes.JOBS
            ),
            create_approvals_toolset(max_retries=5).filtered(
                filter_func=lambda ctx, _: cast(Deps, ctx.deps).agent_mode == AgentModes.APPROVALS
            ),
        ],
    )
    return agent