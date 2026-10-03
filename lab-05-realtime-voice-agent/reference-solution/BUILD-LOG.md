# Build log

## Prompt 1: Scaffold the Python project

- Created the installable `realtime_voice_agent` Python package scaffold and
  declared the voice SDK, NumPy, development, and optional microphone
  dependencies.
- Added setup documentation, environment example, ignore rules, demo entry
  point, and offline scaffold tests.
- Documented the distinction between the Python SDK `VoicePipeline` and
  browser JavaScript realtime sessions, with links to the OpenAI voice agents
  and audio guides.
- Verification: `uv run --extra dev pytest -q` — passed (2 tests).

## Prompt 2: Add the voice agent and tool

- Added `build_voice_agent() -> Agent` using the Agents SDK directly and a
  function-call-safe `voice_course_assistant` name with the `gpt-6-luna`
  default model.
- Added the SDK `@function_tool` named `lookup_lab_answer` and a deterministic
  lookup helper for `voicepipeline`, `traces`, and `tools` topics.
- Added offline checks for the real SDK `Agent`, tool name safety, and stable
  lookup results.
- Verification: `uv run --extra dev pytest -q` — passed (5 tests); no API
  calls were made.

## Prompt 3: Add the voice pipeline

- Added `build_voice_pipeline()` with the SDK `VoicePipeline`,
  `SingleAgentVoiceWorkflow`, `VoicePipelineConfig`, and callback types. The
  config retains workflow tracing metadata and disables sensitive audio
  payload tracing.
- Added `TranscriptCapture`, deterministic static int16 silence input,
  optional fixed-duration microphone capture and response playback helpers,
  and event summaries.
- Microphone support reports the requested `uv sync` and `uv run` commands
  when `sounddevice` is unavailable.
- Verification: `uv run --extra dev pytest -q` — passed (9 tests). Tests only
  construct SDK objects and exercise local helpers; no STT, TTS, or model calls.

## Prompt 4: Add the runnable demo

- Connected `run_reference.py` to the package CLI with `--seconds`, `--record`,
  and `--no-playback` options. Generated silence remains the default static
  `AudioInput`; microphone response playback is enabled by default.
- Added a clean exit when `OPENAI_API_KEY` is missing, captured transcription
  and streamed event reporting, and a trace-inspection hint.
- Documented both requested microphone commands in the README.
- Verification: `./.venv/bin/pytest -q` — passed (10 tests). With the key
  removed, `env -u OPENAI_API_KEY ./.venv/bin/python run_reference.py` printed
  the skip message and exited 0. Tests and this skip-path run made no API calls.

## Prompt 5: Add the browser Realtime agent

- Added an independent TypeScript browser app using `RealtimeAgent` and
  `RealtimeSession` with `gpt-realtime-2`, audio-only output, explicit input
  transcription, and low-eagerness semantic VAD.
- Added start/stop controls, microphone permission, optional typed input, and
  event logging that suppresses empty user transcripts, buffers assistant
  transcript deltas until completion, and ignores `history_updated` events.
- Added a trusted Express `/token` route. It calls the Realtime client secrets
  endpoint with the server-only API key and `OpenAI-Safety-Identifier`, and
  returns only the ephemeral secret to the browser.
- Documented that browser WebRTC Realtime and Python `VoicePipeline` are
  alternative architectures. The Vite dev server uses plain HTTP on localhost,
  a secure browser context for local microphone access.
- Verification: `npm test` — passed (4 tests); `npm run typecheck` — passed;
  `npm run build` — passed. Tests construct SDK objects without connecting and
  test token parsing/request construction without OpenAI API calls.

## Local browser certificate adjustment

- Switched Vite from its self-signed HTTPS certificate to HTTP on `localhost`.
  Browsers treat localhost as a secure context, which permits microphone access
  without a locally trusted certificate. Updated the browser README and lockfile
  accordingly.
- Vite serves at `http://localhost:5173/` without a certificate warning.

## Replay takeover verification

- Set the reusable Python Agents SDK `Agent` default model to `gpt-6-luna` and
  aligned the browser and token server on `gpt-realtime-2` as specified by the
  lab prompt pack.
- `./.venv/bin/python -m pytest -q`: passed (10 tests).
- `env -u OPENAI_API_KEY ./.venv/bin/python run_reference.py`: printed the
  clean skip message and exited 0.
- `npm test`: passed (4 tests); `npm run typecheck`: passed;
  `npm run build`: passed.
- Current guidance was checked in the OpenAI Docs MCP:
  [Voice agents](https://developers.openai.com/api/docs/guides/voice-agents)
  recommends selecting a chained pipeline when each speech and text stage
  should be inspectable or replaceable and identifies the Realtime browser
  session as a distinct speech-to-speech architecture. The
  [Audio and voice guide](https://developers.openai.com/api/docs/guides/audio)
  maps an existing text agent to the Voice agents chained workflow and a
  speech-to-speech agent to the Realtime session path.
