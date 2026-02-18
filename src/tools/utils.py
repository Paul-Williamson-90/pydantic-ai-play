from typing import Callable

from pydantic_ai import RunContext, ToolDefinition

from src.enums import AgentModes
from src.deps import Deps


def prepare_only_if_agent_mode(agent_mode: AgentModes) -> Callable[[RunContext[Deps], ToolDefinition], ToolDefinition | None]:
    async def only_if_agent_mode(
        ctx: RunContext[Deps], tool_def: ToolDefinition
    ) -> ToolDefinition | None:
        if ctx.deps.agent_mode.value == agent_mode.value:
            return tool_def
    return only_if_agent_mode