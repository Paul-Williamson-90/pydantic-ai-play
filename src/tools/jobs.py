from datetime import datetime
import json

from pydantic import BaseModel, Field
from pydantic_ai import ToolReturn, RunContext, ModelRetry, FunctionToolset, Tool

from src.deps import Deps
from src.schemas import JobCreate, JobUpdate, JobDelete, Job, JobStatus


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
    
    
class ListFilter(BaseModel):
    limit: int = Field(default=10, description="Maximum number of items to return")
    offset: int = Field(default=0, description="Number of items to skip before starting to collect the result set")
    gte_date: datetime | None = Field(default=None, description="Filter items with a date greater than or equal to this value")
    lte_date: datetime | None = Field(default=None, description="Filter items with a date less than or equal to this value")
    status: list[JobStatus] | None = Field(default=None, description="Filter items with a specific status")
    
    
async def get_jobs(ctx: RunContext[Deps], filters: ListFilter) -> ToolReturn:
    """Get all existing jobs from the list of jobs in the dependencies."""
    if not ctx.deps.jobs:
        return ToolReturn(
            return_value="No jobs found",
        )
    ctx.deps.event_history.append("Retrieved all jobs")
    jobs = ctx.deps.jobs
    if filters.gte_date:
        jobs = [job for job in jobs if job.deadline >= filters.gte_date]
    if filters.lte_date:
        jobs = [job for job in jobs if job.deadline <= filters.lte_date]
    if filters.status:
        jobs = [job for job in jobs if job.status in filters.status]
    return ToolReturn(
        return_value=f"Found {len(jobs)} jobs",
        content=[job.model_dump(mode="json") for job in jobs],
    )
    
    
def create_jobs_toolset(**tools_kwargs) -> FunctionToolset[Deps]:
    return FunctionToolset(
        tools=[
            Tool(function=add_job, name="add_job", description="Add a new job with a name and deadline", **tools_kwargs),
            Tool(function=update_job, name="update_job", description="Update an existing job with new data", **tools_kwargs),
            Tool(function=delete_job, name="delete_job", description="Delete an existing job by ID", **tools_kwargs),
            Tool(function=get_job, name="get_job", description="Get an existing job by ID", **tools_kwargs),
            Tool(function=get_jobs, name="get_jobs", description="Get all existing jobs with optional filters", **tools_kwargs),
        ],
    )
