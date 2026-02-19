from enum import Enum

from pydantic import BaseModel, Field

from src.utils import prefixed_uuid


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    
    
class Approval(BaseModel):
    id: str = Field(default_factory=lambda: prefixed_uuid("approval"))
    person: str = Field(..., description="Name of the person required to approve the request")
    request: str = Field(..., description="Description of the request that needs approval")
    status: ApprovalStatus = Field(..., description="Current status of the approval request")
    job_id: str | None = Field(None, description="ID of the related job, if applicable")
    
    
class ApprovalCreate(BaseModel):
    person: str = Field(..., description="Name of the person required to approve the request")
    request: str = Field(..., description="Description of the request that needs approval")
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Current status of the approval request")
    job_id: str | None = Field(None, description="ID of the related job, if applicable")
    
    
class ApprovalUpdate(BaseModel):
    id: str = Field(..., description="ID of the approval to update")
    person: str | None = Field(None, description="Name of the person required to approve the request")
    request: str | None = Field(None, description="Description of the request that needs approval")
    status: ApprovalStatus | None = Field(None, description="Current status of the approval request")
    
    
class ApprovalDelete(BaseModel):
    id: str = Field(..., description="ID of the approval to delete")