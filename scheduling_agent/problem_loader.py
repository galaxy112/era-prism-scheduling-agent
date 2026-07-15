from __future__ import annotations

import json
from pathlib import Path

from .models import BatchSpec, DowntimeWindow, Problem, StepSpec


def load_problem(path: str | Path) -> Problem:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Problem(
        resources=list(data["resources"]),
        downtimes=[
            DowntimeWindow(
                resource=item["resource"],
                start=int(item["start"]),
                end=int(item["end"]),
            )
            for item in data.get("downtimes", [])
        ],
        batches=[
            BatchSpec(
                batch_id=item["batch_id"],
                deadline=int(item["deadline"]),
                steps=[
                    StepSpec(resource=step["resource"], duration=int(step["duration"]))
                    for step in item["steps"]
                ],
            )
            for item in data["batches"]
        ],
    )
