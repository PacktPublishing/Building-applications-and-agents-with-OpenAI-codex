# Lab 08 build log

Built on 2026-09-03 by following CI-01 through CI-04 in the lab prompt pack.

## CI-01 — Synthetic CSV and source verification

- Read repository instructions and openai-agents-sdk core/testing guidance.
- Verified hosted Code Interpreter, explicit containers, expiration, and
  container file citation downloads through official OpenAI documentation.
- Inspected the official SDK `examples/tools/code_interpreter.py` at commit
  `9411cee8e2fc8e3656e4f9b8f7eec370a943f2ea` and installed SDK type definitions.
- Environment: Python 3.12, openai-agents 0.17.2, openai 2.36.0.
- Added deterministic synthetic CSV generation and local schema validation.
- No OPENAI_API_KEY is available; hosted chart generation cannot run in this build.
- Ran `../../.venv/bin/python generate_data.py` and
  `../../.venv/bin/python -m unittest discover -s tests -v`: **3 tests passed**.
  The committed fixture contains 36 rows and reproduces byte-for-byte.

## CI-02 — Agent, container, and lifecycle

- Added direct Agent, CodeInterpreterTool, ModelSettings, Runner.run, and
  RunConfig with a Responses provider and lab tracing metadata.
- The runner uploads the CSV and creates an explicit 1 GB container, records
  resource IDs, reports actual tool calls/code/usage, and cleans up in finally.
- Added recovery cleanup and no-key checks. Container deletion correctly
  handles the installed SDK's None return value.
- `../../.venv/bin/python -m unittest discover -s tests -v`: **9 tests passed**.

## CI-03 — Actual artifact download path

- Added typed extraction of completed Code Interpreter calls and container
  file citations, deduplication, fixed output names, and container-scoped downloads.
- Invalid/missing/ambiguous artifacts fail visibly; no fallback chart is created.
- Added PNG-byte and totals-schema checks, plus mocked full-flow and failure tests.
- Verified downloads happen before cleanup, known resources are cleaned up after
  model/download failures, and cleanup failures preserve both state and artifacts.
- `../../.venv/bin/python -m unittest discover -s tests -v`: **19 tests passed**.

## CI-04 — Learner materials, live gate, and integration

- Added the lab brief, README, guided diagram exercise, source verification,
  and complete replay prompt pack, all as Markdown.
- Linked Lab 08 from the repository README, prompt index, runner/test guides,
  and replay README; preserved prior Lab 06 and Lab 07 work.
- Added an opt-in live smoke test checking completed Code Interpreter execution,
  PNG header/dimensions, twelve exact monthly totals, and remote cleanup. It
  retains real output files for visual review when credentials are available.
- Final suite: **19 offline tests passed; 1 live test skipped**.
- Explicit live selection with RUN_CODE_INTERPRETER_SMOKE=1 and the key removed:
  **1 skipped** with a missing-key message. No live model/container calls ran.
- Ran --help, run --help, run, and cleanup in separate processes with no key:
  all exited 0; API commands printed SKIP and created no output directory.
- Verified **27 local Markdown link targets**, byte-for-byte replay prompt
  parity, and `git diff --check`.
- The synthetic CSV is included. No real Code Interpreter diagram was generated
  during this build; hosted execution and visual chart quality remain to be
  verified using the documented live command with credentials.

## Model alignment update

- Set the text Agent/SandboxAgent default to `gpt-6-luna`; retained specialized voice and transcription models where applicable.
- Offline verification after the update: 19 passed, 1 skipped.
