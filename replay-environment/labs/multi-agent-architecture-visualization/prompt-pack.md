# Prompt Pack: Chapter 10, Lab 11

Use these prompts in order. Build under
`solutions/multi-agent-architecture-visualization/`. Do not inspect or copy
reference solutions from other labs. Use the repo-local SDK skill and its
official checkout. Set all three Agents to `gpt-6-luna`.

## Prompt 1 — Define the architecture

```text
Create three real OpenAI Agents SDK Agent objects for an intake → research →
response-writer workflow. Configure the intake agent with one real SDK handoff
to the research agent, and the research agent with one real SDK handoff to the
writer. This must yield exactly two directed handover edges. Set the model on
each agent to gpt-6-luna. Add a helper that returns the root intake Agent so
the SDK visualization can recursively discover its handoff graph. Do not run
the agents or call the API.
```

## Prompt 2 — Export PNG with the SDK visualization extension

```text
Add an exporter using `draw_graph` from `agents.extensions.visualization`.
Install the `openai-agents[viz]` extra. The script should generate a PNG at
outputs/multi-agent-handoffs.png (create the output directory), print its
absolute path, and accept an optional output path. Use draw_graph's filename
argument and account for its behavior of adding the `.png` extension. Document
the native Graphviz executable requirement and setup commands for macOS and
Debian/Ubuntu. The command must work without OPENAI_API_KEY.
```

## Prompt 3 — Test architecture and exported image

```text
Add offline tests for the real SDK Agent objects, the exact two handoffs, and
the graph source edges. When the Graphviz `dot` executable is available, render
the PNG and verify its PNG signature; skip only the render check if `dot` is
unavailable. Document setup, run command, output path, and the two-hop
architecture. Record prompt steps and actual verification in BUILD-LOG.md.
```

## Prompt 4 — Review

```text
Review the architecture, exporter, tests, README, and build log. Run local
tests, verify the PNG when Graphviz is installed, and record the actual
outcome. The visualization is static and must not call the model.
```
