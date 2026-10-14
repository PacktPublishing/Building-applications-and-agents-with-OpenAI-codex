from __future__ import annotations

from agents import RunConfig


def build_run_config() -> RunConfig:
    return RunConfig(
        workflow_name="lab-04-handoffs-patterns",
        trace_metadata={"lab": "04", "course": "mastering-openai-agents"},
    )
