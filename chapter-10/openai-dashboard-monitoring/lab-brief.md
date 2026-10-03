# Chapter 10 · Lab 10: Monitor Agent Runs in the OpenAI Dashboard

## Goal

Build one OpenAI Agents SDK agent that uses two local MCP tools, then inspect
its tool calls and related traces in the OpenAI dashboard.

## What You Build

- A local stdio MCP server with a deterministic mock weather lookup for five
  fixed cities.
- A deterministic mock public swimming pool opening-hours lookup for the
  fictional town of Riverton.
- One SDK `Agent` that can use both MCP tools.
- Two separate `Runner.run` calls sharing a trace `group_id`, so their traces
  can be located together in the dashboard.

## OpenAI Agents Concepts

- `MCPServerStdio` and local MCP tools
- `Agent.mcp_servers`
- `Runner.run` and `RunConfig`
- SDK tracing, `group_id`, workflow name, and metadata
- Dashboard trace and tool-call inspection

## Checkpoint

Run both prompts, find each trace in the OpenAI dashboard, and confirm both
traces share the same group ID. Expand the trace spans to inspect the local MCP
tool names, inputs, outputs, and model response.

All town, pool, and weather data is synthetic and must be labeled as mock data.
