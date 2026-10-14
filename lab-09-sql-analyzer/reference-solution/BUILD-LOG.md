# Build Log: Lab 09

## Prompts Used

- Source prompt pack: `prompt-pack.md`.
- Course alignment prompt: verify SDK-first structure, read-only SQL tools,
  structured output, optional API-backed execution, and Markdown materials.

## Verification

- OpenAI docs verification recorded in `docs/openai-docs-verification.md`.
- Reference implementation moved into this Lab 09 `reference-solution/`
  folder so the lab structure matches the rest of the course.
- Added explicit `build_run_config()` and passed it into `Runner.run(...)`.
- Refactored database access into SDK run context:
  `Runner.run(..., context=SqlAnalyzerContext(...))`, with database-backed
  tools receiving `ctx: RunContextWrapper[SqlAnalyzerContext]`.
- Updated prompt pack so recreating Lab 09 asks for run-context dependency
  injection instead of environment mutation.
- Fixed `AnalysisAnswer` to be strict JSON schema compatible by replacing
  open-ended `dict[str, Any]` final rows with ordered value arrays matching the
  `columns` field.
- Verification: `uv run pytest -q` -> 17 passed, 1 skipped.

## Model alignment update

- Set the text Agent/SandboxAgent default to `gpt-6-luna`; retained specialized voice and transcription models where applicable.
- Offline verification after the update: 18 passed, 1 skipped.

## SQL Analyzer model configuration alignment (2026-10-05)

- Confirmed `get_model()` already defaults to `gpt-6-luna`.
- Aligned `.env.example` with that default and documented it in the README.
- Verification: `../../.venv/bin/python -m pytest -q` -> 18 passed, 1 skipped.
- `uv run pytest -q` was blocked by the existing workspace configuration:
  the sandbox lab (now Lab 08) was listed as a member but had no `pyproject.toml`.

## SDK 0.23.1 update

- Raised the OpenAI Agents SDK floor to `openai-agents>=0.23.1` (resolved
  0.23.1 with `openai` 3.31.0). Offline tests pass; live API tests were not rerun.

## Renumbering — Lab 04 to Lab 09

- Renamed `lab-04-sql-analyzer/` (temporarily `lab-004-sql-analyzer/`) to
  `lab-09-sql-analyzer/`, and the replay prompt pack folder to
  `replay-environment/labs/lab-09-sql-analyzer/`.
- Updated titles, `workflow_name`, trace metadata, the agent contract test,
  README paths, prompt packs, and repository-level guides to Lab 09.
