from typing import Any

from pydantic_ai import FunctionToolset, ToolReturn, RunContext, Tool

from src.enums import SelectableAgentModes, AgentModes, convert_selectable_agent_mode_to_agent_mode
from src.deps import Deps


def job_dynamic_context(ctx: RunContext[Deps]) -> dict[str, Any]:
    current_jobs_dict = {
        job.id: job.name for job in ctx.deps.jobs
    }
    if not current_jobs_dict:
        return {"message": "There are currently no jobs."}
    return {
        "message": f"There are currently {len(current_jobs_dict)} jobs.",
        "jobs_id_to_name": current_jobs_dict,
    }
    
    
def approval_dynamic_context(ctx: RunContext[Deps]) -> dict[str, Any]:
    current_approvals_dict = {
        approval.id: {
            "request": approval.request,
            "linked_job_id": approval.job_id,
            "status": approval.status.value,
            "person": approval.person,
        } for approval in ctx.deps.approvals
    }
    if not current_approvals_dict:
        return {"message": "There are currently no approvals setup."}
    return {
        "message": f"There are currently {len(current_approvals_dict)} approvals.",
        "approvals_id_to_request": current_approvals_dict,
    }


async def route_to_agent(ctx: RunContext[Deps], agent_mode: SelectableAgentModes) -> ToolReturn:
    """
    Switch to an agent mode to handle the user's request.
    Each agent mode has access to specific tools appropriate for that mode.
    """
    ctx.deps.agent_mode = convert_selectable_agent_mode_to_agent_mode(agent_mode)
    
    dynamic_context = None
    match agent_mode.value:
        case AgentModes.JOBS.value:
            dynamic_context = job_dynamic_context(ctx)
        case AgentModes.APPROVALS.value:
            dynamic_context = approval_dynamic_context(ctx)
        case AgentModes.ESTIMATIONS.value:
            pass # TODO
        case _:
            pass # No additional context needed for ROUTER mode
    
    return ToolReturn(
        return_value="Switched to agent mode: " + agent_mode.value,
        content=dynamic_context,
    )


root_to_agent_tool = Tool(route_to_agent, max_retries=5)


router_toolset = FunctionToolset(tools=[root_to_agent_tool])