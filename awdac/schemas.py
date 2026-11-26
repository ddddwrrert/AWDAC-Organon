import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


@dataclass(frozen=True)
class Condition:
    task: str
    evaluator: str
    environment: str
    parameters: str
    protocol: str
    seeds: tuple[int, ...]
    direction: Literal["min", "max"]
    purpose: Literal["official", "diagnostic"] = "official"

    def __post_init__(self):
        if not all((self.task, self.evaluator, self.environment, self.parameters, self.protocol)):
            raise ValueError("Evaluation identity is incomplete")
        if self.direction not in ("min", "max") or self.purpose not in ("official", "diagnostic"):
            raise ValueError("Invalid evaluation direction or purpose")
        if not self.seeds or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("Expected a unique, nonempty seed schedule")


@dataclass(frozen=True)
class Seed:
    id: int
    score: float | None
    runtime: float | None = None
    feasible: bool | None = None
    status: str = "success"
    features: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Proposal:
    hypothesis: str
    observation: str


@dataclass(frozen=True)
class Intent:
    mode: Literal["incremental", "structural", "radical"]
    hypothesis: str
    observation: str
    design: str
    benefit: str
    risk: str
    validation: str
    rebuttal: str = ""
    operator_actions: tuple[str, ...] = ()

    def __post_init__(self):
        if self.mode not in ("incremental", "structural", "radical"):
            raise ValueError("Unknown rewrite mode")


@dataclass(frozen=True)
class Candidate:
    source: str
    intent: Intent | None = None
