from typing import Any

from dataclasses import dataclass, field

from ..schemas import Job, Approval


@dataclass
class Deps:
    jobs: list[Job] = field(default_factory=list)
    approvals: list[Approval] = field(default_factory=list)
    max_messages: int = 15
    reduce_messages_to: int = 10
    
    subagents: dict[str, Any] = field(default_factory=dict)

    def clone_for_subagent(self, max_depth: int = 0) -> "Deps":
        return Deps(subagents={} if max_depth <= 0 else self.subagents.copy())