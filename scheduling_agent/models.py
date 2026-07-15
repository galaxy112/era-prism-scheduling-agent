from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class StepSpec:
    resource: str
    duration: int


@dataclass(frozen=True)
class BatchSpec:
    batch_id: str
    deadline: int
    steps: List[StepSpec]


@dataclass(frozen=True)
class DowntimeWindow:
    resource: str
    start: int
    end: int


@dataclass(frozen=True)
class Problem:
    resources: List[str]
    downtimes: List[DowntimeWindow]
    batches: List[BatchSpec]


@dataclass
class ScheduledStep:
    batch_id: str
    step_index: int
    resource: str
    duration: int
    start: int
    end: int
    deadline: int

    def label(self) -> str:
        return f"{self.batch_id}.{self.step_index}:{self.resource}[{self.start},{self.end})"


@dataclass
class ValidationIssue:
    kind: str
    message: str
    steps: List[str] = field(default_factory=list)


@dataclass
class ScoreBreakdown:
    hard_errors: int
    makespan: int
    total_tardiness: int
    score: int


Schedule = List[ScheduledStep]
ResourceAvailability = Dict[str, int]
