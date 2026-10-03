# Prompt Pack: Chapter 10, Lab 10


Default all SDK Agent/SandboxAgent model settings to `gpt-6-luna`. Keep modality-specific transcription, speech, and realtime audio model IDs unchanged.

Follow these prompts in order. Create the reference implementation in
`reference-solution/`. Keep the lab's prompt pack complete and replayable.

## Prompt 1 — Local mock MCP server

```text
Create a Python reference solution for this lab. Start with a local stdio MCP
server using the official Python MCP SDK FastMCP. Expose exactly two
deterministic tools: get_mock_weather(city) and get_public_pool_hours(town,
weekday). The weather tool supports exactly five fixed cities (Berlin, London,
New York, Tokyo, Sydney) and clearly labels the result as mock data. The pool
tool supports one fictional town, Riverton, with a small explicit weekly
schedule for its fictional public pools, and labels results as mock data. Keep
tool functions independently testable. Add README setup and verification notes.
```

## Prompt 2 — SDK agent and trace grouping

```text
Add a direct OpenAI Agents SDK Agent that connects to the local MCP server via
MCPServerStdio. Add a runnable demo that makes two Runner.run calls through the
agent: one asks for weather, one asks about Riverton pool hours. Pass an SDK
RunConfig to both calls with a shared group_id and descriptive workflow_name
and trace_metadata. Print final_output for each. The run must use OPENAI_API_KEY
and skip cleanly when it is absent. Close the MCP server with its async context
manager. Document how to find both related traces in OpenAI Dashboard → Logs →
Agents (or Traces if that view is enabled for the account), and how to inspect
the MCP tool spans and group ID. Do not claim mock data is live information.
```

## Prompt 3 — Offline contract tests

```text
Add offline tests that require no API key and no model calls. Verify the two
mock datasets, supported inputs, invalid-input handling, Agent SDK object and
MCP server wiring, and RunConfig workflow_name, trace_metadata, and shared
group_id. Add an API integration test that skips cleanly without
OPENAI_API_KEY and runs the demo with credentials. Record prompts and actual
verification results in reference-solution/BUILD-LOG.md.
```

## Prompt 4 — Replay and chapter navigation

```text
Review the new lab brief, README, prompt pack, and runnable demo for consistent
Chapter 10 wording and accurate dashboard instructions. Add this lab to the
repository README, prompts index, run-reference guide, and reference test guide
without reorganizing or renaming existing labs. Add a matching replay prompt
pack under replay-environment/labs/openai-dashboard-monitoring and
document the replay output path under solutions/. Do not inspect or copy any
other reference solution while replaying this prompt pack.
```
