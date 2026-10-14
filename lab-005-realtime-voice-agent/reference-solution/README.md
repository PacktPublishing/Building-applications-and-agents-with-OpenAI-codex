# Lab 05: Realtime Voice Agent

This project is the Python scaffold for the voice-agent lab. Its Python path
will reuse a text agent through the OpenAI Agents SDK `VoicePipeline`: audio is
transcribed, passed through the agent workflow, and synthesized as speech.

Browser speech-to-speech realtime sessions are a different architecture and
transport path. They use JavaScript realtime agents and a live session (for
example, over WebRTC); they are not the Python `VoicePipeline` path.

## Setup

Install the project and development tools with [uv](https://docs.astral.sh/uv/):

```sh
uv sync --extra dev
```

For optional local microphone capture support:

```sh
uv sync --extra dev --extra mic
```

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` when running the
API-backed demo. Local tests are designed not to make API calls.

## Documentation note

The [OpenAI voice agents guide](https://developers.openai.com/api/docs/guides/voice-agents)
describes the architecture choices: chained voice pipelines provide control
over speech-to-text, agent reasoning, and text-to-speech stages, while Realtime
API sessions handle speech and reasoning in a live session. The
[OpenAI audio guide](https://developers.openai.com/api/docs/guides/audio)
recommends choosing the path based on the application: a voice interface for
an existing text agent can use a voice pipeline, while speech-to-speech
applications can use a Realtime session. Python reuse of an existing text
agent therefore belongs on the SDK `VoicePipeline` path; browser realtime
speech-to-speech belongs on its JavaScript and transport path.

## Run

Set `OPENAI_API_KEY` in your shell (or load it from your local `.env`) and run
the API-backed demo. Without the key, the command exits cleanly without making
an API request.

```sh
uv run python run_reference.py --seconds 1
```

With the microphone extra installed, capture four seconds of speech. Response
audio plays by default:

```sh
uv run --extra mic python run_reference.py --record --seconds 4
```

For a silent run, including classroom or CI environments, use:

```sh
uv run --extra mic python run_reference.py --record --seconds 4 --no-playback
```

Without `--record`, the demo submits generated silence as static `AudioInput`.

The separate JavaScript browser implementation is in
[`realtime-browser/`](realtime-browser/README.md). It keeps a live WebRTC
session open and is an alternate architecture to this Python pipeline.
