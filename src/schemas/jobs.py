from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from src.utils import prefixed_uuid


class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    id: str = Field(default_factory=lambda: prefixed_uuid("job"))
    name: str = Field(..., description="Name of the job")
    deadline: datetime = Field(..., description="Deadline for the job")
    status: JobStatus = Field(..., description="Current status of the job")
    
    
class JobCreate(BaseModel):
    name: str = Field(..., description="Name of the job")
    deadline: datetime = Field(..., description="Deadline for the job")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current status of the job")
    
    
class JobUpdate(BaseModel):
    id: str = Field(..., description="ID of the job to update")
    name: str | None = Field(None, description="Name of the job")
    deadline: datetime | None = Field(None, description="Deadline for the job")
    status: JobStatus | None = Field(None, description="Current status of the job")
    
    
class JobDelete(BaseModel):
    id: str = Field(..., description="ID of the job to delete")