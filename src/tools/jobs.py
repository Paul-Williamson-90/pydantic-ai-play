import json

from pydantic_ai import FunctionToolset, ToolReturn, RunContext, Tool, ModelRetry

from src.enums import AgentModes
from src.deps import Deps
from src.schemas import JobCreate, JobUpdate, JobDelete, Job

from .utils import prepare_only_if_agent_mode


async def add_job(ctx: RunContext[Deps], job: JobCreate) -> ToolReturn:
    """Create a new job with the given name and deadline, and add it to the list of jobs in the dependencies."""
    new_job = Job(
        **job.model_dump(),
    )
    ctx.deps.jobs.append(new_job)
    ctx.deps.event_history.append(f"Added job with ID: {new_job.id}")
    return ToolReturn(
        return_value="Created a new job called: " + job.name,
        content=json.dumps(new_job.model_dump(mode="json")),
    )
    
    
async def update_job(ctx: RunContext[Deps], job: JobUpdate) -> ToolReturn:
    """Update an existing job with the given ID and new data."""
    data = job.model_dump(exclude_unset=True)
    existing_job = next((j for j in ctx.deps.jobs if j.id == job.id), None)
    if not existing_job:
        return ModelRetry("Job not found with ID: " + job.id)
    for key, value in data.items():
        setattr(existing_job, key, value)
    ctx.deps.event_history.append(f"Updated job with ID: {existing_job.id}")
    return ToolReturn(
        return_value="Updated job with ID: " + job.id,
        content=json.dumps(existing_job.model_dump(mode="json")),
    )
    
    
async def delete_job(ctx: RunContext[Deps], job: JobDelete) -> ToolReturn:
    """Delete an existing job with the given ID from the list of jobs in the dependencies."""
    existing_job = next((j for j in ctx.deps.jobs if j.id == job.id), None)
    if not existing_job:
        return ModelRetry("Job not found with ID: " + job.id)
    ctx.deps.jobs.remove(existing_job)
    ctx.deps.event_history.append(f"Deleted job with ID: {existing_job.id}")
    return ToolReturn(
        return_value="Deleted job with ID: " + job.id,
        content=json.dumps(existing_job.model_dump(mode="json")),
    )
    
    
async def get_job(ctx: RunContext[Deps], job_id: str) -> ToolReturn:
    """Get an existing job with the given ID from the list of jobs in the dependencies."""
    existing_job = next((j for j in ctx.deps.jobs if j.id == job_id), None)
    if not existing_job:
        return ModelRetry("Job not found with ID: " + job_id)
    ctx.deps.event_history.append(f"Retrieved job with ID: {existing_job.id}")
    return ToolReturn(
        return_value="Found job with ID: " + job_id,
        content=json.dumps(existing_job.model_dump(mode="json")),
    )


add_job_tool = Tool(add_job, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)
update_job_tool = Tool(update_job, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)
delete_job_tool = Tool(delete_job, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)
get_job_tool = Tool(get_job, prepare=prepare_only_if_agent_mode(AgentModes.JOBS), max_retries=5)


jobs_toolset = FunctionToolset(tools=[add_job_tool, update_job_tool, delete_job_tool, get_job_tool])