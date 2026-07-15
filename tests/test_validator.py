import unittest

from scheduling_agent.models import DowntimeWindow, Problem, ScheduledStep
from scheduling_agent.validator import validate_schedule


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.problem = Problem(
            resources=["MIXER", "INCUBATOR"],
            downtimes=[DowntimeWindow("INCUBATOR", 8, 10)],
            batches=[],
        )

    def test_detects_resource_conflict(self):
        schedule = [
            ScheduledStep("A", 0, "MIXER", 4, 0, 4, 10),
            ScheduledStep("B", 0, "MIXER", 3, 3, 6, 10),
        ]
        issues = validate_schedule(schedule, self.problem)
        self.assertIn("resource_conflict", {issue.kind for issue in issues})

    def test_detects_step_order_error(self):
        schedule = [
            ScheduledStep("A", 0, "MIXER", 4, 4, 8, 10),
            ScheduledStep("A", 1, "INCUBATOR", 2, 6, 8, 10),
        ]
        issues = validate_schedule(schedule, self.problem)
        self.assertIn("step_order", {issue.kind for issue in issues})

    def test_detects_downtime_conflict(self):
        schedule = [ScheduledStep("A", 0, "INCUBATOR", 5, 5, 10, 12)]
        issues = validate_schedule(schedule, self.problem)
        self.assertIn("downtime_conflict", {issue.kind for issue in issues})


if __name__ == "__main__":
    unittest.main()
