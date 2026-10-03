"""Command-line runner for the API-backed Python voice pipeline demo."""

from __future__ import annotations

import argparse
import asyncio
import os
from collections.abc import Sequence

import numpy as np

from .agent import build_voice_agent
from .voice import (
    TranscriptCapture,
    build_voice_pipeline,
    make_silence_audio,
    play_response_audio,
    record_microphone_audio,
    summarize_voice_event,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Lab 05 Python voice pipeline demo.")
    parser.add_argument(
        "--seconds", type=float, default=1.0, help="Static input audio length in seconds."
    )
    parser.add_argument(
        "--record", action="store_true", help="Capture microphone audio instead of silence."
    )
    parser.add_argument(
        "--no-playback",
        action="store_true",
        help="Do not play response audio (useful for CI and silent environments).",
    )
    return parser


async def _run_demo(seconds: float, record: bool, playback: bool) -> int:
    capture = TranscriptCapture()
    pipeline = build_voice_pipeline(build_voice_agent(), callbacks=capture)
    if record:
        print(f"Recording microphone input for {seconds:g} seconds...")
        audio_input = record_microphone_audio(seconds)
    else:
        print(
            "Using generated silence as static AudioInput. "
            "Pass --record to capture microphone input."
        )
        audio_input = make_silence_audio(seconds)

    result = await pipeline.run(audio_input)
    response_chunks: list[np.ndarray] = []
    async for event in result.stream():
        print(summarize_voice_event(event))
        if event.type == "voice_stream_event_audio" and event.data is not None:
            response_chunks.append(event.data)

    if capture.transcriptions:
        for transcription in capture.transcriptions:
            print(f"Transcription: {transcription}")
    else:
        print("Transcription: (none captured)")

    if playback and record and response_chunks:
        print("Playing response audio...")
        play_response_audio(response_chunks)
    elif not response_chunks:
        print("No response audio chunks were produced.")
    else:
        print("Response audio playback is disabled or not requested.")

    print("Inspect workflow traces in the OpenAI dashboard under Traces.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.seconds <= 0:
        print("--seconds must be greater than zero.")
        return 2
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set; skipping the API-backed voice demo.")
        return 0
    try:
        return asyncio.run(_run_demo(args.seconds, args.record, not args.no_playback))
    except KeyboardInterrupt:
        print("Voice demo interrupted.")
        return 130

