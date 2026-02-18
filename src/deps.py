from collections import deque
from dataclasses import dataclass, field

from src.enums import AgentModes
from src.schemas import Job


@dataclass
class Deps:
    agent_mode: AgentModes = AgentModes.ROUTER
    jobs: list[Job] = field(default_factory=list)
    event_history: deque[str] = field(default_factory=lambda: deque(maxlen=10))