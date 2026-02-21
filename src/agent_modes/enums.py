from enum import Enum


class AgentModes(str, Enum):
    ROUTER = "router"
    JOBS = "jobs"
    APPROVALS = "approvals"
    ESTIMATIONS = "estimations"
    
    
class SelectableAgentModes(str, Enum):
    JOBS = "jobs"
    APPROVALS = "approvals"
    # ESTIMATIONS = "estimations"
    
    
def convert_agent_mode_to_selectable(agent_mode: AgentModes) -> SelectableAgentModes | None:
    match agent_mode.value:
        case AgentModes.JOBS.value:
            return SelectableAgentModes.JOBS
        case AgentModes.APPROVALS.value:
            return SelectableAgentModes.APPROVALS
        # case AgentModes.ESTIMATIONS.value:
        #     return SelectableAgentModes.ESTIMATIONS
        case _:
            return None
        
def convert_selectable_agent_mode_to_agent_mode(selectable_agent_mode: SelectableAgentModes) -> AgentModes:
    match selectable_agent_mode.value:
        case SelectableAgentModes.JOBS.value:
            return AgentModes.JOBS
        case SelectableAgentModes.APPROVALS.value:
            return AgentModes.APPROVALS
        # case SelectableAgentModes.ESTIMATIONS.value:
        #     return AgentModes.ESTIMATIONS
        case _:
            raise ValueError("Invalid selectable agent mode: " + selectable_agent_mode.value)