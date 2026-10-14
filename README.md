# Building Applications and Agents with OpenAI Codex

Use this repository to learn the OpenAI Agents SDK through Codex-built
reference solutions.

Codex is the construction partner. OpenAI Agents and SandboxAgents are the
subject matter. Every lab ships a reproducible Codex prompt pack and a finished
reference solution, so you can either rebuild a lab with Codex or study and run
the result directly.

The reference implementations are SDK-first: Lab 00 teaches Codex workflow,
Labs 01-07, 09, and 10 use direct OpenAI Agents SDK `Agent` flows, and Lab 08
uses direct SDK `SandboxAgent` with Unix-local `SandboxRunConfig`.

## Labs

The labs are numbered in the suggested order. Each title links to the lab brief.

| Lab | Title | What you learn |
|---|---|---|
| 00 | [Codex Workflow](lab-00-codex-workflow/lab-brief.md) | Drive Codex as an agentic developer before building agents |
| 01 | [Agent Basics](lab-01-agent-basics/lab-brief.md) | Touch the core SDK primitives: `Agent`, `Runner`, tools, guardrails, sessions, and structured output |
| 02 | [OpenAI Vector Store](lab-02-vector-store/lab-brief.md) | Build document Q&A with hosted retrieval, file citations, and resource cleanup |
| 03 | [CSV to Diagram with Code Interpreter](lab-03-code-interpreter/lab-brief.md) | Turn synthetic sales data into a downloadable chart using hosted Python execution |
| 04 | [Handoffs Patterns](lab-04-handoffs-patterns/lab-brief.md) | Compare handoffs and agents-as-tools |
| 05 | [Monitor Agent Runs in the OpenAI Dashboard](lab-05-openai-dashboard-monitoring/lab-brief.md) | Connect two local mock MCP tools and group related agent traces with a shared `group_id` |
| 06 | [Visualize a Multi-Agent Handoff Architecture](lab-06-multi-agent-architecture-visualization/lab-brief.md) | Draw two successive SDK handoffs and export a PNG with `openai-agents[viz]` |
| 07 | [Realtime Voice Agent](lab-07-realtime-voice-agent/lab-brief.md) | Compare Python voice pipelines with browser realtime sessions |
| 08 | [SandboxAgent Sampler](lab-08-sandboxagent/lab-brief.md) | Use a sandboxed workspace, shell, skills, memory, and resumption |
| 09 | [SQL Analyzer Agent](lab-09-sql-analyzer/lab-brief.md) | Build a full business reference solution with read-only SQL tools and run context |
| 10 | [Interactive Agent REPL](lab-10-repl/lab-brief.md) | Test conversation history and streaming in a terminal |

### Suggested path

1. Start with Lab 00 for the Codex workflow and Lab 01 for the SDK primitives.
   Later labs assume the Lab 01 basics.
2. Labs 02 and 03 add hosted tools: `FileSearchTool` over a vector store and
   `CodeInterpreterTool` for generated files.
3. Labs 04-06 cover multi-agent orchestration and observability: handoffs and
   agents-as-tools, grouped traces in the OpenAI dashboard, and handoff graphs.
4. Lab 07 reuses normal `Agent` objects in Python voice and browser realtime
   architectures.
5. Lab 08 moves to `SandboxAgent` with a Unix-local sandbox.
6. Lab 09 brings these ideas together in a full business reference solution.
7. Lab 10 is a short optional exercise you can take any time after Lab 01.

## Requirements

- Python 3.11+ and [uv](https://docs.astral.sh/uv/).
- OpenAI Agents SDK `openai-agents` 0.23.1 or newer. The locked workspace
  installs it for you.
- An `OPENAI_API_KEY` for demos and smoke tests that call OpenAI. Offline tests
  run without one.
- Lab 06: the Graphviz `dot` executable (for example `brew install graphviz`).
- Lab 07 browser example: Node.js 20 or newer and npm.

All text-based Agent and SandboxAgent references default to `gpt-6-luna`.
Lab 07's speech, transcription, and browser realtime paths keep their
modality-specific audio models.

## Setup

Clone the repository with submodules so the SDK reference checkout is available
inside the repo-local skill:

```bash
git clone --recurse-submodules https://github.com/PacktPublishing/Building-applications-and-agents-with-OpenAI-codex.git
cd Building-applications-and-agents-with-OpenAI-codex
```

If you already cloned without submodules, initialize them once:

```bash
git submodule update --init --recursive
```

Install the locked workspace dependencies from the repository root:

```bash
uv sync --frozen
```

This one environment covers Labs 00-04 and 07-10. Labs 05 and 06 each have their
own `requirements.txt`; see the [run guide](run-reference-guide.md) for their
setup.

Provide your API key by exporting it, or by putting it in a `.env` file at the
repository root. Most lab entry points load `.env` automatically, and it is
git-ignored.

```bash
export OPENAI_API_KEY="sk-..."
```

## Run and Test the References

- [run-reference-guide.md](run-reference-guide.md) shows how to run each lab's
  demo interactively.
- [reference-test-guide.md](reference-test-guide.md) covers the two test
  layers: offline contract tests, which do not call OpenAI, and OpenAI API smoke
  tests, which require `OPENAI_API_KEY` and can be forced with
  `REQUIRE_OPENAI_API=1`.

Without `OPENAI_API_KEY`, API-backed demos print a message and stop before
calling OpenAI.

## Reproducible Prompts and Replay

Each lab's `prompt-pack.md` is a reproducible Codex build script, indexed in
[prompts-index.md](prompts-index.md). Each reference solution includes a
`BUILD-LOG.md` recording the prompt IDs and local verification.

To rebuild a lab from scratch with Codex, use the
[replay environment](replay-environment/README.md). It contains the prompt
packs, course rules, and the repo-local SDK skill, but no finished solutions.

## Repository Layout

```text
lab-<number>-<topic>/
  lab-brief.md          # goal, concepts, and status
  prompt-pack.md        # reproducible Codex build prompts
  reference-solution/   # finished implementation, tests, and BUILD-LOG.md
replay-environment/     # clean space for replaying prompt packs with Codex
  .agents/skills/openai-agents-sdk/
    openai-agents-python/   # official SDK checkout (Git submodule)
  labs/<lab-name>/prompt-pack.md
AGENTS.md               # course implementation rules for Codex
```

The submodule points to the official
[`openai/openai-agents-python`](https://github.com/openai/openai-agents-python)
repository. The course pins a known SDK commit for reproducibility; update that
pin intentionally with `git submodule update --remote` and rerun the lab tests.
