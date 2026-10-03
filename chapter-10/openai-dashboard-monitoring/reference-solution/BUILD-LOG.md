# Build Log

## Prompt steps

- Prompt 1: Added deterministic mock weather and public pool data plus a local
  stdio MCP server exposing two tools.
- Prompt 2: Added an SDK `Agent` using `gpt-6-luna`, two `Runner.run` calls, and
  shared trace grouping configuration.
- Prompt 3: Added offline contract tests for fixture behavior and SDK contracts.
- Prompt 4: Added Chapter 10 lab/replay navigation without moving existing labs.

## Verification

- `uv run --with pytest --with pytest-asyncio --with openai-agents --with 'mcp>=1.19,<2' pytest -q`: **5 passed, 1 skipped**. The skipped API integration test requires `OPENAI_API_KEY`.
- The same dependency-scoped `uv run ... python run_reference.py` command printed the expected clean skip because `OPENAI_API_KEY` is absent.
- Live API run was not performed as part of local verification.
