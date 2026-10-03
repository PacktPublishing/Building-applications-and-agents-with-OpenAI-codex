# Lab 06 build log

Built 2026-09-03 by following the lab-level prompt pack in order.

## Sources and environment

- Read the labs repository AGENTS.md and its repo-local openai-agents-sdk skill.
- Inspected the official checkout at
  `replay-environment/.agents/skills/openai-agents-sdk/openai-agents-python/src/agents/repl.py`.
- Inspected the installed `run_demo_loop` signature with Python:
  `(agent, *, stream=True, context=None, max_turns=10)`.
- Verified installed distribution: `openai-agents==0.17.2`.
- Consulted the public SDK REPL guide. An OpenAI Docs MCP search for
  `run_demo_loop` returned no hits; the official SDK source supplies the
  implementation details.

## REPL-01 — Minimal agent

Created `run_reference.py` using a real `Agent` and `run_demo_loop`, with
conversation-only shopping-list instructions and a missing-key skip.
Reviewed the implementation against the SDK helper signature.

## REPL-02 — Stream option

Added `--no-stream` and a startup hint. From the repository root, ran:

```bash
.venv/bin/python lab-06-repl/reference-solution/run_reference.py --help
env -u OPENAI_API_KEY .venv/bin/python lab-06-repl/reference-solution/run_reference.py
env -u OPENAI_API_KEY .venv/bin/python lab-06-repl/reference-solution/run_reference.py --no-stream
```

All exited successfully. Help showed the flag; both no-key commands printed
the skip message without starting the interactive loop.

## REPL-03 — Offline tests

Added four unittest methods covering default/overridden models, real SDK
Agent construction, both stream modes, and absent/blank credentials.
From this solution directory, ran:

```bash
../../.venv/bin/python -m unittest discover -s tests -v
```

Result: **4 tests passed**. No API calls were made.

## REPL-04 — Runbook

Added setup, pinned requirements, manual exercises, expected outcomes,
history limitations, and an acceptance checklist. Added the lab brief and
registered the prompt pack in the repository and replay indexes.

Final checks: local Markdown links resolve; reference and replay prompt packs
are byte-identical; `git diff --check` passed.

Live model conversations have **not** been run. Shopping-list behavior and
interactive rendering remain manual acceptance checks; the offline results
do not establish those outcomes.

## Model alignment update

- Set the text Agent/SandboxAgent default to `gpt-6-luna`; retained specialized voice and transcription models where applicable.
- Offline verification after the update: 4 passed.
