from enum import Enum


class AgentModes(str, Enum):
    ROUTER = "router"
    JOBS = "jobs"
    APPROVALS = "approvals"
    ESTIMATIONS = "estimations"
    
    
class SelectableAgentModes(str, Enum):
    JOBS = "jobs"
    # APPROVALS = "approvals"
    # ESTIMATIONS = "estimations"