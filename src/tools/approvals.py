import json

from pydantic_ai import FunctionToolset, ToolReturn, RunContext, Tool, ModelRetry

from src.enums import AgentModes
from src.deps import Deps
from src.schemas import Approval, ApprovalCreate, ApprovalUpdate, ApprovalDelete

from .utils import prepare_only_if_agent_mode


async def add_approval(ctx: RunContext[Deps], approval: ApprovalCreate) -> ToolReturn:
    """Create a new approval request with the given person, request description, and related job ID, and add it to the list of approvals in the dependencies."""
    new_approval = Approval(
        **approval.model_dump(),
    )
    ctx.deps.approvals.append(new_approval)
    ctx.deps.event_history.append(f"Added approval with ID: {new_approval.id}")
    return ToolReturn(
        return_value="Created a new approval request for: " + new_approval.person,
        content=json.dumps(new_approval.model_dump(mode="json")),
    )
    
    
async def update_approval(ctx: RunContext[Deps], approval: ApprovalUpdate) -> ToolReturn:
    """Update an existing approval request with the given ID and new data."""
    data = approval.model_dump(exclude_unset=True)
    existing_approval = next((a for a in ctx.deps.approvals if a.id == approval.id), None)
    if not existing_approval:
        return ModelRetry("Approval not found with ID: " + approval.id)
    for key, value in data.items():
        setattr(existing_approval, key, value)
    ctx.deps.event_history.append(f"Updated approval with ID: {existing_approval.id}")
    return ToolReturn(
        return_value="Updated approval with ID: " + approval.id,
        content=json.dumps(existing_approval.model_dump(mode="json")),
    )
    
    
async def delete_approval(ctx: RunContext[Deps], approval: ApprovalDelete) -> ToolReturn:
    """Delete an existing approval request with the given ID from the list of approvals in the dependencies."""
    existing_approval = next((a for a in ctx.deps.approvals if a.id == approval.id), None)
    if not existing_approval:
        return ModelRetry("Approval not found with ID: " + approval.id)
    ctx.deps.approvals.remove(existing_approval)
    ctx.deps.event_history.append(f"Deleted approval with ID: {existing_approval.id}")
    return ToolReturn(
        return_value="Deleted approval with ID: " + approval.id,
        content=json.dumps(existing_approval.model_dump(mode="json")),
    )
    
    
async def get_approval(ctx: RunContext[Deps], approval_id: str) -> ToolReturn:
    """Get an existing approval request with the given ID from the list of approvals in the dependencies."""
    existing_approval = next((a for a in ctx.deps.approvals if a.id == approval_id), None)
    if not existing_approval:
        return ModelRetry("Approval not found with ID: " + approval_id)
    ctx.deps.event_history.append(f"Retrieved approval with ID: {existing_approval.id}")
    return ToolReturn(
        return_value="Found approval with ID: " + approval_id,
        content=json.dumps(existing_approval.model_dump(mode="json")),
    )


add_approval_tool = Tool(add_approval, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)
update_approval_tool = Tool(update_approval, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)
delete_approval_tool = Tool(delete_approval, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)
get_approval_tool = Tool(get_approval, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)


approvals_toolset = FunctionToolset(tools=[add_approval_tool, update_approval_tool, delete_approval_tool, get_approval_tool])