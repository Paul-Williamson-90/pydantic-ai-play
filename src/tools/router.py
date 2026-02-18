from pydantic_ai import FunctionToolset, ToolReturn, RunContext, Tool

from src.enums import SelectableAgentModes
from src.deps import Deps


async def route_to_agent(ctx: RunContext[Deps], agent_mode: SelectableAgentModes) -> ToolReturn:
    """
    Switch to an agent mode to handle the user's request.
    Each agent mode has access to specific tools appropriate for that mode.
    """
    ctx.deps.agent_mode = agent_mode
    return ToolReturn("Switched to agent mode: " + agent_mode.value)


root_to_agent_tool = Tool(route_to_agent, max_retries=5)


router_toolset = FunctionToolset(tools=[root_to_agent_tool])