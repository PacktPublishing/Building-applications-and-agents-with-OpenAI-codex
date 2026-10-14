# Build Log

## Prompt steps

- Prompt 1: Added deterministic mock weather and public pool data plus a local
  stdio MCP server exposing two tools.
- Prompt 2: Added an SDK `Agent` using `gpt-6-luna`, two `Runner.run` calls, and
  shared trace grouping configuration.
- Prompt 3: Added offline contract tests for fixture behavior and SDK contracts.
- Prompt 4: Added lab/replay navigation without moving existing labs.

## Verification

- `uv run --with pytest --with pytest-asyncio --with openai-agents --with 'mcp>=1.19,<2' pytest -q`: **5 passed, 1 skipped**. The skipped API integration test requires `OPENAI_API_KEY`.
- The same dependency-scoped `uv run ... python run_reference.py` command printed the expected clean skip because `OPENAI_API_KEY` is absent.
- Live API run was not performed as part of local verification.

## SDK 0.23.1 update

- Raised the OpenAI Agents SDK floor to `openai-agents>=0.23.1` (resolved
  0.23.1 with `openai` 3.31.0). Offline tests pass; live API tests were not rerun.

## Renumbering — Chapter 10 to Lab 05

- Moved `chapter-10/openai-dashboard-monitoring/` to `lab-05-openai-dashboard-monitoring/`, and the replay prompt pack folder to
  `replay-environment/labs/lab-05-openai-dashboard-monitoring/`.
- Updated titles, the trace `group_id`, `workflow_name`, trace metadata, MCP
  server names, contract tests, prompt packs, and repository-level guides to Lab 05.
