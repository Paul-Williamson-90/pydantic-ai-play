from dataclasses import dataclass, field

from .enums import AgentModes
from ..schemas import Job, Approval


@dataclass
class Deps:
    agent_mode: AgentModes = AgentModes.ROUTER
    jobs: list[Job] = field(default_factory=list)
    approvals: list[Approval] = field(default_factory=list)
    max_messages: int = 15
    reduce_messages_to: int = 10