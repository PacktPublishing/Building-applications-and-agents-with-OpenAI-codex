# Build Log: Lab 04

## Prompts Used

- Source prompt pack: `prompt-pack.md`.
- Course alignment prompt: verify SDK-first structure, read-only SQL tools,
  structured output, optional API-backed execution, and Markdown materials.

## Verification

- OpenAI docs verification recorded in `docs/openai-docs-verification.md`.
- Reference implementation moved into this Lab 04 `reference-solution/`
  folder so the lab structure matches the rest of the course.
- Added explicit `build_run_config()` and passed it into `Runner.run(...)`.
- Refactored database access into SDK run context:
  `Runner.run(..., context=SqlAnalyzerContext(...))`, with database-backed
  tools receiving `ctx: RunContextWrapper[SqlAnalyzerContext]`.
- Updated prompt pack so recreating Lab 04 asks for run-context dependency
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
  Lab 03 is listed as a member but has no `pyproject.toml`.
