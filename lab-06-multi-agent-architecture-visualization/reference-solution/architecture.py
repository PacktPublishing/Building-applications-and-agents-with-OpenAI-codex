"""Construct a static three-agent workflow with exactly two handovers."""

from agents import Agent


def build_architecture() -> Agent:
    writer = Agent(
        name="Response writer",
        instructions="Turn verified research notes into a clear, concise response.",
        model="gpt-6-luna",
    )
    researcher = Agent(
        name="Research agent",
        instructions="Research the request, then hand verified notes to the response writer.",
        model="gpt-6-luna",
        handoffs=[writer],
    )
    intake = Agent(
        name="Intake agent",
        instructions="Clarify the request and hand it to the research agent.",
        model="gpt-6-luna",
        handoffs=[researcher],
    )
    return intake
