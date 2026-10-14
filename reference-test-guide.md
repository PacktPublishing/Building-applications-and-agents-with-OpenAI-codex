# Reference Test Guide

The reference suite has two layers.

## 1. Offline Contract Tests

These tests do not call OpenAI. They validate deterministic tools, fixtures,
schemas, SDK object construction, `RunConfig`, and the UnixLocal SandboxAgent
configuration.

```bash
for d in Building-applications-and-agents-with-OpenAI-codex/lab-{00,01,04,07,003}-*/reference-solution; do
  echo "== $d"
  (cd "$d" && uv run --with pytest pytest -q) || exit 1
done

cd Building-applications-and-agents-with-OpenAI-codex/lab-004-sql-analyzer/reference-solution
uv run --with pytest pytest -q
```

## 2. OpenAI API Smoke Tests

These tests call the OpenAI API for Labs 01, 04, 07, 003, and 004. Lab 006 uses a manual live exercise. Set `OPENAI_API_KEY` first.
Set `REQUIRE_OPENAI_API=1` so missing credentials fail instead of skipping.

```bash
export OPENAI_API_KEY="sk-..."
export REQUIRE_OPENAI_API=1

for d in Building-applications-and-agents-with-OpenAI-codex/lab-{01,04,07,003}-*/reference-solution; do
  echo "== $d"
  (cd "$d" && uv run --with pytest pytest -q tests/test_openai_integration.py) || exit 1
done

cd Building-applications-and-agents-with-OpenAI-codex/lab-004-sql-analyzer/reference-solution
uv run --with pytest pytest -q
```

Lab 004 includes an API-backed test in
`lab-004-sql-analyzer/reference-solution`; it skips only when `OPENAI_API_KEY`
is absent.

## What This Proves

- Offline tests prove the references are structurally correct and deterministic
  logic is reliable.
- OpenAI API smoke tests prove each SDK lab actually reaches OpenAI through
  `Runner.run(...)`.
- Lab 003 proves the SandboxAgent path reaches OpenAI while using UnixLocal
  `SandboxRunConfig`.

## Lab 02 vector store checks

From the repository root with the existing synced environment:

```bash
cd lab-02-vector-store/reference-solution
../../.venv/bin/python -m unittest discover -s tests -v
```

The suite checks SDK objects, actual response-model parsing, API argument
forwarding, indexing failures/timeouts, cleanup recovery, and no-key behavior.
The live test skips by default even if credentials exist. Opt in explicitly:

```bash
RUN_VECTOR_STORE_SMOKE=1 REQUIRE_OPENAI_API=1 ../../.venv/bin/python -m unittest discover -s tests -p test_openai_integration.py -v
```

This creates a temporary store and three fictional uploads, checks filtered
retrieval and an agent answer with file citations, and attempts cleanup in
`finally`. A failed cleanup prints the retained manifest path. See the
[lab runbook](lab-02-vector-store/reference-solution/README.md#verification).

## Lab 03 Code Interpreter checks

From the repository root with the existing synced environment:

```bash
cd lab-03-code-interpreter/reference-solution
../../.venv/bin/python -m unittest discover -s tests -v
```

Offline tests cover the synthetic CSV, SDK contracts, container file citations,
download validation, cleanup after failures, and a complete mocked runner path.
They do not execute hosted Python or create a real sales chart.

Explicitly opt into the live test with credentials:

```bash
RUN_CODE_INTERPRETER_SMOKE=1 REQUIRE_OPENAI_API=1 ../../.venv/bin/python -m unittest discover -s tests -p test_openai_integration.py -v
```

It verifies real Code Interpreter execution, downloaded PNG header/dimensions,
all twelve monthly totals against independent Decimal arithmetic, and cleanup.
The chart is retained for visual inspection. See the
[Code Interpreter verification guide](lab-03-code-interpreter/reference-solution/README.md#verification).

## Lab 05 dashboard monitoring checks

Offline checks require no OpenAI API calls:

```bash
cd lab-05-openai-dashboard-monitoring/reference-solution
uv run --with pytest pytest -q
```

The demo is API-backed and skips cleanly without `OPENAI_API_KEY`. With a key,
it sends two runs through the local MCP server. Inspect the resulting traces
and the shared `group_id` in the OpenAI dashboard.

## Lab 06 handoff visualization checks

```bash
cd lab-06-multi-agent-architecture-visualization/reference-solution
uv venv
uv pip install -r requirements.txt
./.venv/bin/python -m pytest -q
./.venv/bin/python export_diagram.py
```

The tests verify the three SDK Agent objects, exactly two handoffs, and both
graph edges. PNG rendering is verified when the system `dot` executable is
installed. The exporter does not make model calls.

## Lab 006 REPL offline checks

From the repository root with the existing synced environment:

```bash
cd lab-006-repl/reference-solution
../../.venv/bin/python -m unittest discover -s tests -v
```

Live behavior is checked with the [manual REPL exercise](lab-006-repl/lab-brief.md);
mocked offline checks do not prove model responses.
