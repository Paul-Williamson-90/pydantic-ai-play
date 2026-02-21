from typing import Any

from pydantic_ai import Agent, RunContext, ModelMessage, FunctionToolset
from subagents_pydantic_ai import create_subagent_toolset, SubAgentConfig

from .deps import Deps
from .tools import create_approvals_toolset, create_jobs_toolset
from ..utils import model_factory
    
    
def get_system_prompt() -> str:
    return (
        "You are a helpful assistant that provides information to users based on their requests. "
        "You can only help the user via tool calls and responding with information. "
        "All information must come from the tools you use and the context available to you. "
        "Do not invent information or tools. "
        
        # NOTE: Below is required in system prompt else the agent doesn't know what the sub-agent ids are
        "To help you with this task, you can call on sub-agents that specialise in different areas: "
        "\n- jobs_agent: Handles operations related to creating, updating, deleting, and retrieving jobs."
        "\n- approvals_agent: Handles operations related to approvals."
    )


def context_processor(
    ctx: RunContext[Deps],
    messages: list[ModelMessage],
) -> list[ModelMessage]:
    if len(messages) >= ctx.deps.max_messages:
        messages = messages[-ctx.deps.reduce_messages_to:]
    return messages


def prepare_sub_agents() -> FunctionToolset[Any]:
    subagents: list[SubAgentConfig] = [
        SubAgentConfig(
            name="jobs_agent",
            model="openai:gpt-5.2",
            description="Handles operations related to creating, updating, deleting, and retrieving jobs.",
            instructions="You specialise in managing job-related tasks, including creating, updating, deleting, and retrieving jobs.",
            can_ask_questions=True,
            preferred_mode="async",
            typical_complexity="simple",
            toolsets=[create_jobs_toolset()],
            typically_needs_context=True,
            # context_files=["/agents/coder/AGENTS.md", "/CODING_RULES.md"]
        ),
        SubAgentConfig(
            name="approvals_agent",
            model="openai:gpt-5.2",
            description="Handles operations related to approvals.",
            instructions="You specialise in managing approval-related tasks, including creating, updating, deleting, and retrieving approvals.",
            can_ask_questions=True,
            preferred_mode="async",
            typical_complexity="simple",
            toolsets=[create_approvals_toolset()],
            typically_needs_context=True,
            # context_files=["/agents/coder/AGENTS.md", "/CODING_RULES.md"]
        ),
    ]
    subagents_toolset = create_subagent_toolset(subagents=subagents, id="core_agent_subagents")
    return subagents_toolset


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
            prepare_sub_agents()
        ],
    )
    return agent