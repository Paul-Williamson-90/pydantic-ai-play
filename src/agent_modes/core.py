from typing import cast

from pydantic_ai import Agent, RunContext, ModelMessage

from .deps import Deps
from .tools import (
    create_router_toolset,
    create_approvals_toolset,
    create_jobs_toolset,
)
from .enums import AgentModes
from ..utils import model_factory
    
    
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
        model=model_factory(),
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