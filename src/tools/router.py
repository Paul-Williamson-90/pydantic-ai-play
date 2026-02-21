from pydantic_ai import ToolReturn, RunContext, FunctionToolset, Tool

from ..enums import SelectableAgentModes, convert_selectable_agent_mode_to_agent_mode
from ..deps import Deps


async def route_to_agent(ctx: RunContext[Deps], agent_mode: SelectableAgentModes) -> ToolReturn:
    """
    Switch to an agent mode to handle the user's request.
    Each agent mode has access to specific tools appropriate for that mode.
    """
    ctx.deps.agent_mode = convert_selectable_agent_mode_to_agent_mode(agent_mode)
    
    return ToolReturn(
        return_value="Switched to agent mode: " + agent_mode.value,
    )
    
    
def create_router_toolset(**tools_kwargs) -> FunctionToolset[Deps]:
    return FunctionToolset(
        tools=[
            Tool(
                function=route_to_agent, 
                name="route_to_agent", 
                description="Route to a specific agent mode to handle the user's request and retrieve additional context for that mode if needed", 
                **tools_kwargs
            ),
        ],
    )
    