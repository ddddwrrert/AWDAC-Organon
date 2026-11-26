from typing import Protocol
from ..schemas import Proposal, Candidate

class Worker(Protocol):
    def propose(self, context: dict, advice: Proposal | None) -> Candidate: ...
