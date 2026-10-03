# Lab 07 build log

Built on 2026-09-03 by following the lab-level prompt pack in order.

## VS-01 — Scaffold

- Read repository AGENTS.md, the requested and repo-local openai-agents-sdk
  skills, core SDK/testing references, and official file search example.
- Verified the official file search and retrieval guides through OpenAI Docs.
- Installed environment: Python 3.12, openai-agents 0.17.2, openai 2.36.0.
- Official SDK checkout: `9411cee8e2fc8e3656e4f9b8f7eec370a943f2ea`.
- Created pinned requirements and three fictional Markdown policy fixtures.
- No OPENAI_API_KEY is available in this build environment.

## VS-02 — Resource lifecycle

- Implemented create, upload, bounded indexing, and cleanup through AsyncOpenAI.
- Persisted IDs after each creation/deletion; failed operations retain retry state.
- Ran `../../.venv/bin/python -m unittest discover -s tests -v` from this folder:
  **11 offline tests passed**, including failure, timeout, and cleanup retry cases.

## VS-03 — Direct retrieval and hosted tool

- Added ingest/search/ask/cleanup CLI commands, a direct SDK Agent and
  FileSearchTool, Runner.run, and RunConfig with a Responses model provider.
- Added category filters, returned chunks, actual file citation annotations,
  and token usage reporting. API exception bodies are not echoed.
- `../../.venv/bin/python run_reference.py --help` passed.
- `../../.venv/bin/python -m unittest discover -s tests -v`:
  **23 offline tests passed**. Missing/blank credentials skip every command
  without creating a client; mocked Runner calls receive real SDK objects.

## VS-04 — Optional hosted smoke test

- Added an explicitly gated live test covering filtered direct retrieval and
  real agent search results/citations. Cleanup runs in finally and retains the
  manifest if it fails.
- Full suite: **23 offline tests passed; 1 live test skipped**.
- Explicitly selected the live test with RUN_VECTOR_STORE_SMOKE=1 and no key:
  **1 skipped** with a missing-key message, as intended.
- No files were uploaded and no model calls were made during this build.

## VS-05 — Learner materials and repository integration

- Added the reference README, guided lab exercises, lab brief, and official
  source verification record, all as Markdown.
- Linked Lab 07 from the repository README, prompt index, runner/test guides,
  and replay README while preserving the pre-existing Lab 06 work.
- Copied the complete prompt pack to the replay labs directory; byte-for-byte
  parity verified.
- Ran --help and all four commands in separate processes with the key removed:
  each exited 0; API commands printed SKIP and created no resource manifest.
- Verified 24 local Markdown link targets across the lab and repository guides.
- `git diff --check` passed. Reviewed the new reference and guide changes.
- Final verification: **23 offline tests passed; 1 live test skipped**.
  Hosted retrieval, model answer quality, and real cleanup remain unverified
  until the documented opt-in live test is run with credentials.

## Model alignment update

- Set the text Agent/SandboxAgent default to `gpt-6-luna`; retained specialized voice and transcription models where applicable.
- Offline verification after the update: 23 passed, 1 skipped.
