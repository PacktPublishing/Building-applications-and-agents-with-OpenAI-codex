"""One SDK Agent and a deterministic, synthetic course information tool."""

import os

from agents import Agent, RunConfig, function_tool


def course_info(topic: str) -> str:
    """Look up a topic in the fictional course catalog."""
    catalog = {
        "agents": "Agents: define an Agent, call Runner.run, and add function tools.",
        "deployment": "Deployment: package an ARM64 image and host it on AgentCore Runtime.",
        "observability": "Observability: instrument SDK spans and export them with ADOT to CloudWatch.",
    }
    return "Synthetic course data. " + catalog.get(
        topic.strip().lower(), "Unknown topic. Choose agents, deployment, or observability."
    )


@function_tool
def get_course_info(topic: str) -> str:
    """Return synthetic course information for agents, deployment, or observability."""
    return course_info(topic)


def build_agent() -> Agent:
    return Agent(
        name="course_assistant",
        instructions=(
            "Help with the fictional course catalog. For course questions, always call "
            "get_course_info before answering. Label course information as synthetic. "
            "Give a short answer grounded in the tool output."
        ),
        model=os.getenv("OPENAI_MODEL", "gpt-6-luna"),
        tools=[get_course_info],
    )


def build_run_config(session_id: str) -> RunConfig:
    return RunConfig(
        workflow_name="chapter10_lab12_agentcore",
        group_id=session_id,
        trace_metadata={"lab": "12", "hosting": "agentcore", "data": "synthetic"},
        # The instrumentation library consumes SDK tracing callbacks. Disabling
        # SDK tracing here would also suppress its agent/model/tool spans.
        tracing_disabled=False,
        trace_include_sensitive_data=True,
    )
