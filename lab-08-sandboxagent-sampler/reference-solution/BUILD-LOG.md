# Build Log: Lab 08 SandboxAgent Sampler

## Prompt steps

- Prompt 1: Added the tiny calculator repo, its intentionally failing test,
  and a smoke check for the SDK manifest's validated relative entries.
- Prompt 2: Added SandboxAgent instructions to inspect, test, fix, and verify
  the calculator, then write and reread durable notes in root-level `memories/`.
- Prompt 3: Added the `debug-failing-tests` skill.
- Prompt 4: Seeded file-based memory locally and in the relative manifest,
  explicitly configured SDK `Memory`, and documented the two-run worksheet.
- Prompt 5: Added explicit `Filesystem`, `Shell`, `Skills`, and `Memory`
  capabilities, UnixLocal configuration and live-session helpers, and local
  SDK contract checks.
- Prompt 6: Added streamed and non-streamed runner paths, `--model` and
  `--max-turns` options, snapshot support, and finally-path close/export/delete
  cleanup.
- Prompt 7: Added `run_memory_demo.py`, which reuses one unique `LocalSnapshot`
  across two fresh runs with distinct trace group IDs. It verifies that the
  first raw memory survives unchanged and both raw memories have matching
  rollout summaries.

## Verification

- `python -m py_compile` on the lab's Python files: passed.
- `python -m pytest -q tests` in the solution directory using the realtime voice
  lab's virtual environment: passed (4 tests).
- `python check_manifest.py`: passed; relative manifest and seeded Memory
  configuration validated.
- `python -m py_compile sandbox_manifest.py sandbox_instructions.py
  run_sandbox_demo.py run_memory_demo.py check_manifest.py`: passed.
- API-backed demos require `OPENAI_API_KEY`; they are not part of local test
  verification.

## SDK 0.23.1 update

- Raised the OpenAI Agents SDK floor to `openai-agents>=0.23.1` (resolved
  0.23.1 with `openai` 3.31.0). Offline tests pass; live API tests were not rerun.

## Renumbering — Lab 03 to Lab 08

- Renamed `lab-03-sandboxagent-sampler/` (temporarily
  `lab-003-sandboxagent-sampler/`) to `lab-08-sandboxagent-sampler/`, and the
  replay prompt pack folder to `replay-environment/labs/lab-08-sandboxagent-sampler/`.
- Updated titles, `workflow_name` values, instructions, the calculator repo's
  AGENTS.md, prompt packs, and repository-level guides to Lab 08.
