from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Schedule


def schedule_to_protocol(schedule: Schedule) -> list[dict[str, Any]]:
    return [
        {
            "batch_id": step.batch_id,
            "step_index": step.step_index,
            "resource": step.resource,
            "duration": step.duration,
            "start": step.start,
            "end": step.end,
            "deadline": step.deadline,
        }
        for step in sorted(schedule, key=lambda item: (item.start, item.resource, item.batch_id, item.step_index))
    ]


def write_protocol(schedule: Schedule, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(schedule_to_protocol(schedule), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
