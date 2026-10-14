"""Python Agents SDK voice workflow and local audio helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from agents import Agent
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    SingleAgentWorkflowCallbacks,
    VoicePipeline,
    VoicePipelineConfig,
)


SAMPLE_RATE = 24_000
WORKFLOW_NAME = "lab-05-realtime-voice-agent"
TRACE_METADATA = {"lab": "05", "component": "python_voice_pipeline"}


@dataclass
class TranscriptCapture(SingleAgentWorkflowCallbacks):
    """Collect transcriptions from the SDK single-agent voice workflow."""

    transcriptions: list[str] = field(default_factory=list)

    def on_run(self, workflow: SingleAgentVoiceWorkflow, transcription: str) -> None:
        self.transcriptions.append(transcription)


def build_voice_pipeline(
    agent: Agent,
    callbacks: SingleAgentWorkflowCallbacks | None = None,
) -> VoicePipeline:
    """Create a real SDK voice pipeline with named, metadata-rich tracing."""
    workflow = SingleAgentVoiceWorkflow(agent, callbacks=callbacks)
    config = VoicePipelineConfig(
        workflow_name=WORKFLOW_NAME,
        trace_metadata=dict(TRACE_METADATA),
        trace_include_sensitive_audio_data=False,
    )
    return VoicePipeline(workflow=workflow, config=config)


def make_silence_audio(seconds: float = 1.0) -> AudioInput:
    """Create deterministic mono silence as static int16 audio input."""
    if seconds <= 0:
        raise ValueError("seconds must be greater than zero")
    samples = int(SAMPLE_RATE * seconds)
    return AudioInput(buffer=np.zeros(samples, dtype=np.int16), frame_rate=SAMPLE_RATE)


def _require_sounddevice() -> Any:
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise RuntimeError(
            "Microphone support is missing. Run `uv sync --extra dev --extra mic` "
            "and then `uv run --extra mic python run_reference.py --record --seconds 4`."
        ) from exc
    return sd


def record_microphone_audio(seconds: float) -> AudioInput:
    """Record a fixed duration from the default microphone into static audio."""
    if seconds <= 0:
        raise ValueError("seconds must be greater than zero")
    sd = _require_sounddevice()
    recording = sd.rec(
        int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16"
    )
    sd.wait()
    return AudioInput(buffer=np.asarray(recording, dtype=np.int16).reshape(-1), frame_rate=SAMPLE_RATE)


def play_response_audio(chunks: list[np.ndarray]) -> None:
    """Play collected response chunks; callers can omit this for silent runs."""
    if not chunks:
        return
    sd = _require_sounddevice()
    audio = np.concatenate(chunks)
    if audio.dtype == np.float32:
        audio = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    else:
        audio = audio.astype(np.int16, copy=False)
    sd.play(audio, samplerate=SAMPLE_RATE)
    sd.wait()


def summarize_voice_event(event: Any) -> str:
    """Format SDK lifecycle, audio, and error events for a console demo."""
    if event.type == "voice_stream_event_lifecycle":
        return f"Lifecycle: {event.event}"
    if event.type == "voice_stream_event_audio":
        sample_count = 0 if event.data is None else int(event.data.size)
        return f"Audio chunk: {sample_count} samples"
    if event.type == "voice_stream_event_error":
        return f"Voice pipeline error: {event.error}"
    return f"Voice event: {event.type}"
