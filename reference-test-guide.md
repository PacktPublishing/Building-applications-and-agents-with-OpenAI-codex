# Reference Test Guide

The reference suite has two layers.

## 1. Offline Contract Tests

These tests do not call OpenAI. They validate deterministic tools, fixtures,
schemas, SDK object construction, `RunConfig`, and the UnixLocal SandboxAgent
configuration.

```bash
for d in Building-applications-and-agents-with-OpenAI-codex/lab-{00,01,02,03,05}-*/reference-solution; do
  echo "== $d"
  (cd "$d" && uv run --with pytest pytest -q) || exit 1
done

cd Building-applications-and-agents-with-OpenAI-codex/lab-04-sql-analyzer/reference-solution
uv run --with pytest pytest -q
```

## 2. OpenAI API Smoke Tests

These tests call the OpenAI API for Labs 01–05. Lab 06 uses a manual live exercise. Set `OPENAI_API_KEY` first.
Set `REQUIRE_OPENAI_API=1` so missing credentials fail instead of skipping.

```bash
export OPENAI_API_KEY="sk-..."
export REQUIRE_OPENAI_API=1

for d in Building-applications-and-agents-with-OpenAI-codex/lab-{01,02,03,05}-*/reference-solution; do
  echo "== $d"
  (cd "$d" && uv run --with pytest pytest -q tests/test_openai_integration.py) || exit 1
done

cd Building-applications-and-agents-with-OpenAI-codex/lab-04-sql-analyzer/reference-solution
uv run --with pytest pytest -q
```

Lab 04 includes an API-backed test in
`lab-04-sql-analyzer/reference-solution`; it skips only when `OPENAI_API_KEY`
is absent.

## What This Proves

- Offline tests prove the references are structurally correct and deterministic
  logic is reliable.
- OpenAI API smoke tests prove each SDK lab actually reaches OpenAI through
  `Runner.run(...)`.
- Lab 03 proves the SandboxAgent path reaches OpenAI while using UnixLocal
  `SandboxRunConfig`.

## Lab 06 REPL offline checks

From the repository root with the existing synced environment:

```bash
cd lab-06-repl/reference-solution
../../.venv/bin/python -m unittest discover -s tests -v
```

Live behavior is checked with the [manual REPL exercise](lab-06-repl/lab-brief.md);
mocked offline checks do not prove model responses.

## Lab 07 vector store checks

From the repository root with the existing synced environment:

```bash
cd lab-07-vector-store/reference-solution
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
[lab runbook](lab-07-vector-store/reference-solution/README.md#verification).

## Lab 08 Code Interpreter checks

From the repository root with the existing synced environment:

```bash
cd lab-08-code-interpreter/reference-solution
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
[Code Interpreter verification guide](lab-08-code-interpreter/reference-solution/README.md#verification).

## Chapter 10 Lab 10 dashboard monitoring checks

Offline checks require no OpenAI API calls:

```bash
cd chapter-10/openai-dashboard-monitoring/reference-solution
uv run --with pytest pytest -q
```

The demo is API-backed and skips cleanly without `OPENAI_API_KEY`. With a key,
it sends two runs through the local MCP server. Inspect the resulting traces
and the shared `group_id` in the OpenAI dashboard.

## Chapter 10 Lab 11 handoff visualization checks

```bash
cd chapter-10/multi-agent-architecture-visualization/reference-solution
uv venv
uv pip install -r requirements.txt
./.venv/bin/python -m pytest -q
./.venv/bin/python export_diagram.py
```

The tests verify the three SDK Agent objects, exactly two handoffs, and both
graph edges. PNG rendering is verified when the system `dot` executable is
installed. The exporter does not make model calls.
