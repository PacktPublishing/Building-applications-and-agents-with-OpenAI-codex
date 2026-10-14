"""Direct Agents SDK agent and deterministic lab lookup tool."""

import re

from agents import Agent, function_tool


_LAB_ANSWERS = {
    "voicepipeline": "VoicePipeline chains speech-to-text, an agent workflow, and text-to-speech.",
    "traces": "Workflow traces help inspect and debug voice-agent runs.",
    "tools": "An Agents SDK function_tool lets an agent call deterministic application code.",
}


@function_tool
def lookup_lab_answer(topic: str) -> str:
    """Look up a short, deterministic answer about a voice-agent lab topic."""
    return lookup_answer(topic)


def lookup_answer(topic: str) -> str:
    """Return a deterministic answer for a supported lab topic."""
    normalized_topic = re.sub(r"[\s_-]+", "", topic.strip().lower())
    return _LAB_ANSWERS.get(
        normalized_topic,
        "No lab answer is available for that topic. Try voicepipeline, traces, or tools.",
    )


def build_voice_agent() -> Agent:
    """Build the Lab 05 voice assistant as a real Agents SDK Agent."""
    return Agent(
        name="voice_course_assistant",
        instructions=(
            "You are a concise assistant for a voice-agent course. "
            "Use the lookup_lab_answer tool when asked about course lab topics."
        ),
        model="gpt-6-luna",
        tools=[lookup_lab_answer],
    )
