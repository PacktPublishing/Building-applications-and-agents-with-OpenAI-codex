# Reference Runner Guide

Each lab reference has a `run_reference.py` script for interactive use. Tests
verify the code; runner scripts let you experience the lab.

Set your OpenAI API key before running SDK labs:

```bash
export OPENAI_API_KEY="sk-..."
```

Agent and SandboxAgent examples use `gpt-6-luna` unless a lab documents a
separate audio model for a speech-specific component.

## Lab 00

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-00-codex-workflow/reference-solution
uv run python run_reference.py README.md
```

## Lab 01

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-01-agent-basics/reference-solution
uv run python run_reference.py first-agent
uv run python run_reference.py structured
uv run python run_reference.py tool
uv run python run_reference.py guardrail
uv run python run_reference.py session
```

## Lab 02

From the repository root, using the existing synced environment:

```bash
.venv/bin/python lab-02-vector-store/reference-solution/run_reference.py ingest
.venv/bin/python lab-02-vector-store/reference-solution/run_reference.py search "Can I return unopened coffee after 10 days?"
.venv/bin/python lab-02-vector-store/reference-solution/run_reference.py ask "Can I return unopened coffee after 10 days, and when do next-day orders close?"
.venv/bin/python lab-02-vector-store/reference-solution/run_reference.py cleanup
```

Run each command in order. Without a key, each skips without changing resources.
With a key, ingestion creates a vector store and uploads the bundled fictional
policies. Search and ask reuse that store; cleanup removes it and the original
uploads. See the [vector store runbook](lab-02-vector-store/reference-solution/README.md)
for standalone setup, filters, state recovery, and guided exercises.

## Lab 03

From the repository root, using the existing synced environment:

```bash
.venv/bin/python lab-03-code-interpreter/reference-solution/run_reference.py run
```

The runner uploads the bundled synthetic sales CSV and uses hosted Code
Interpreter to create a monthly revenue PNG diagram and totals CSV. It prints
their download paths under a fresh run folder and cleans up the remote container
and original upload. Without an API key, it skips without creating a chart.

For another compatible synthetic CSV:

```bash
.venv/bin/python lab-03-code-interpreter/reference-solution/run_reference.py run --csv /absolute/path/to/sales.csv
```

See the [Code Interpreter runbook](lab-03-code-interpreter/reference-solution/README.md)
for schema, setup, generated artifact inspection, and cleanup recovery.

## Lab 04

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-04-handoffs-patterns/reference-solution
uv run python run_reference.py handoff
uv run python run_reference.py tools
```

## Lab 05

```bash
cd lab-05-openai-dashboard-monitoring/reference-solution
uv pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
uv run python run_reference.py
```

The runner makes two requests through one local MCP server and prints each
`final_output`. Find both traces under the shared group ID documented in the
[lab README](lab-05-openai-dashboard-monitoring/reference-solution/README.md).

## Lab 06

```bash
cd lab-06-multi-agent-architecture-visualization/reference-solution
uv venv
uv pip install -r requirements.txt
./.venv/bin/python export_diagram.py
```

This makes no API calls and writes `outputs/multi-agent-handoffs.png`. Install
the native Graphviz executable first; see the
[lab README](lab-06-multi-agent-architecture-visualization/reference-solution/README.md).

## Lab 07

Python voice pipeline:

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-07-realtime-voice-agent/reference-solution
uv run python run_reference.py --seconds 1
```

Without `OPENAI_API_KEY`, the voice demo skips cleanly. With a key, it runs a
static `AudioInput` through the SDK `VoicePipeline` and prints lifecycle/audio
stream summaries.

True browser realtime agent:

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-07-realtime-voice-agent/reference-solution/realtime-browser
npm install
npm test
npm run typecheck
npm run build
export OPENAI_API_KEY="sk-..."
npm run server
```

In another terminal:

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-07-realtime-voice-agent/reference-solution/realtime-browser
npm run dev
```

Open the HTTPS Vite URL and start the realtime session in the browser.

## Lab 003

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-003-sandboxagent-sampler/reference-solution
uv run python run_sandbox_demo.py
```

This runs the SandboxAgent through UnixLocal `SandboxRunConfig` and streams
progress events, including model text, tool calls, and tool outputs.

To run without streaming progress:

```bash
uv run python run_sandbox_demo.py --no-stream
```

## Lab 004

```bash
cd Building-applications-and-agents-with-OpenAI-codex/lab-004-sql-analyzer/reference-solution
uv run python run_reference.py
```

Use the SQL Analyzer README for CLI options and custom questions.

## Lab 006

From the repository root, using the existing synced environment:

```bash
.venv/bin/python lab-006-repl/reference-solution/run_reference.py
# After exiting, compare complete replies:
.venv/bin/python lab-006-repl/reference-solution/run_reference.py --no-stream
```

See the [REPL runbook](lab-006-repl/reference-solution/README.md) for standalone
setup and the manual conversation exercise.
