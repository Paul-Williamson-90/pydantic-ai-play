from typing import Callable, Any

from pydantic_ai import RunContext, ToolDefinition, FunctionToolset, Tool

from src.enums import AgentModes
from src.deps import Deps


def prepare_only_if_agent_mode(agent_mode: AgentModes) -> Callable[[RunContext[Deps], ToolDefinition], ToolDefinition | None]:
    async def only_if_agent_mode(
        ctx: RunContext[Deps], tool_def: ToolDefinition
    ) -> ToolDefinition | None:
        if ctx.deps.agent_mode.value == agent_mode.value:
            return tool_def
    return only_if_agent_mode


def create_toolset_for_agent_mode(
    agent_mode: AgentModes, 
    tools: list[Callable], 
    tool_kwargs: dict[str, Any] | None = None, 
    toolset_kwargs: dict[str, Any] | None = None
) -> FunctionToolset:
    prepare_func = prepare_only_if_agent_mode(agent_mode)
    toolset = FunctionToolset(
        tools=[
            Tool(t, prepare=prepare_func, **tool_kwargs or {}) for t in tools
        ],
        **toolset_kwargs or {}
    )
    return toolset