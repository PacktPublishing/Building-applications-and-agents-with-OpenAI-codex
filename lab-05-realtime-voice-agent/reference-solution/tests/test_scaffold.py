from pathlib import Path
import re

import numpy as np
from agents import Agent
from realtime_voice_agent.agent import build_voice_agent, lookup_answer, lookup_lab_answer
from agents.voice import AudioInput, SingleAgentVoiceWorkflow, VoicePipeline
from realtime_voice_agent.voice import (
    SAMPLE_RATE,
    TRACE_METADATA,
    TranscriptCapture,
    build_voice_pipeline,
    make_silence_audio,
    summarize_voice_event,
)
from realtime_voice_agent.cli import main as cli_main


PROJECT = Path(__file__).resolve().parents[1]


def test_package_name_and_dependencies_are_declared() -> None:
    project = (PROJECT / "pyproject.toml").read_text()
    assert 'name = "realtime-voice-agent"' in project
    assert '"openai-agents[voice]"' in project
    assert '"numpy"' in project
    assert '"pytest"' in project
    assert '"pytest-asyncio"' in project
    assert '"sounddevice"' in project


def test_readme_documents_uv_extras_and_architecture_split() -> None:
    readme = (PROJECT / "README.md").read_text()
    assert "uv sync --extra dev" in readme
    assert "uv sync --extra dev --extra mic" in readme
    assert "VoicePipeline" in readme
    assert "JavaScript" in readme


def test_voice_agent_is_a_real_sdk_agent() -> None:
    agent = build_voice_agent()
    assert isinstance(agent, Agent)
    assert agent.name == "voice_course_assistant"
    assert agent.model == "gpt-6-luna"
    assert lookup_lab_answer in agent.tools


def test_lookup_tool_name_is_function_call_safe() -> None:
    assert re.fullmatch(r"[a-z0-9_]+", lookup_lab_answer.name)
    assert lookup_lab_answer.name == "lookup_lab_answer"


def test_lookup_tool_returns_deterministic_answers() -> None:
    assert "speech-to-text" in lookup_answer("voicepipeline")
    assert "traces" in lookup_answer("traces")
    assert "function_tool" in lookup_answer("tools")
    assert lookup_answer("Voice Pipeline") == lookup_answer("voicepipeline")
    unknown = lookup_answer("unknown")
    assert unknown == lookup_answer("unknown")


def test_voice_pipeline_configuration_and_real_sdk_types() -> None:
    capture = TranscriptCapture()
    pipeline = build_voice_pipeline(build_voice_agent(), callbacks=capture)
    assert isinstance(pipeline, VoicePipeline)
    assert isinstance(pipeline.workflow, SingleAgentVoiceWorkflow)
    assert pipeline.workflow._callbacks is capture
    assert pipeline.config.workflow_name == "lab-05-realtime-voice-agent"
    assert pipeline.config.trace_metadata == TRACE_METADATA
    assert pipeline.config.trace_include_sensitive_audio_data is False


def test_transcript_capture_records_local_transcriptions() -> None:
    capture = TranscriptCapture()
    capture.on_run(None, "Explain voice pipelines")
    assert capture.transcriptions == ["Explain voice pipelines"]


def test_silence_audio_is_static_deterministic_int16() -> None:
    audio = make_silence_audio(0.25)
    assert isinstance(audio, AudioInput)
    assert audio.buffer.dtype == np.int16
    assert audio.buffer.shape == (SAMPLE_RATE // 4,)
    assert np.count_nonzero(audio.buffer) == 0
    assert audio.frame_rate == SAMPLE_RATE


def test_voice_event_summaries_cover_audio_and_lifecycle() -> None:
    from agents.voice.events import VoiceStreamEventAudio, VoiceStreamEventLifecycle

    assert summarize_voice_event(VoiceStreamEventLifecycle(event="turn_started")) == "Lifecycle: turn_started"
    assert summarize_voice_event(
        VoiceStreamEventAudio(data=np.zeros(12, dtype=np.int16))
    ) == "Audio chunk: 12 samples"


def test_cli_skips_cleanly_when_api_key_is_absent(monkeypatch, capsys) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert cli_main(["--seconds", "1"]) == 0
    assert "OPENAI_API_KEY is not set" in capsys.readouterr().out
