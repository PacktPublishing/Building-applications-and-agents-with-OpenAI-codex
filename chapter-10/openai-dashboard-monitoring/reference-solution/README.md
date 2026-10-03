# Chapter 10 Lab 10: Monitor Agent Runs in the OpenAI Dashboard

This reference builds one OpenAI Agents SDK `Agent` with a local stdio MCP
server. The server exposes two deterministic synthetic tools: mock weather for
Berlin, London, New York, Tokyo, and Sydney, and opening hours for public pools
in the fictional town of Riverton. The agent explicitly uses `gpt-6-luna`. No
live services are queried.

## Setup and run

From this directory:

```bash
uv venv
uv pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
./.venv/bin/python run_reference.py
```

Without `OPENAI_API_KEY`, the runner prints a clean skip message. Each run
prints the model's `final_output`. Both `Runner.run` calls use the same SDK
`RunConfig.group_id` (`chapter-10-monitoring-demo`), producing separate traces
that can be grouped as one conversation/process in the dashboard.

## Inspect traces

Open [OpenAI Dashboard Logs](https://platform.openai.com/logs) and select the
Agents view or open [Traces](https://platform.openai.com/traces), depending on
the dashboard view available to your account. Find the workflow named
**Chapter 10 mock town services**, then inspect the two runs. The SDK records
the `group_id` and trace metadata (`chapter`, `lab`, and `data`) on each trace.
Open each trace and expand its timeline to review the model generation, local
MCP tool name, arguments, and returned tool output. Dashboard navigation and
filters can vary by account; if group ID is not directly searchable, open one
trace and use its group ID to locate the related trace.

Tracing is enabled by default in the SDK. This demo requires an API key and
makes model calls; its mock weather and pool tool results remain deterministic.

## Offline checks

```bash
./.venv/bin/python -m pytest -q
```

The local tests check fixture values, invalid inputs, direct SDK objects, the
two MCP tool declarations, and trace grouping configuration without model
calls.
