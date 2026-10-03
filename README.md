# Building Applications and Agents with OpenAI Codex

Use this repository to learn the OpenAI Agents SDK through Codex-built
reference solutions.

Codex is the construction partner. OpenAI Agents and SandboxAgents are the
subject matter.

The reference implementations are SDK-first: Lab 00 teaches Codex workflow,
Labs 01-02 and 04-08 use direct OpenAI Agents SDK `Agent` flows, and Lab 03 uses
direct SDK `SandboxAgent` with Unix-local `SandboxRunConfig`.

All text-based Agent and SandboxAgent references explicitly default to
`gpt-6-luna`. Lab 05's speech, transcription, and browser realtime paths retain
their modality-specific audio models.

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

The submodule lives at:

```text
replay-environment/.agents/skills/openai-agents-sdk/openai-agents-python
```

It points to the official
[`openai/openai-agents-python`](https://github.com/openai/openai-agents-python)
repository. The course pins a known SDK commit for reproducibility; update that
pin intentionally with `git submodule update --remote` and rerun the lab tests.

OpenAI Agents Python SDK repository:
<https://github.com/openai/openai-agents-python>

Install Python 3.11+ and [uv](https://docs.astral.sh/uv/), then install the
locked workspace dependencies from the repository root:

```bash
uv sync --frozen
```

The browser realtime example in Lab 05 also requires Node.js and npm.
See its reference README for setup.

## Labs

| Lab | Title | Primary course purpose |
|---|---|---|
| 00 | Codex Workflow | Learn how to drive Codex before building agents |
| 01 | Agents SDK Sampler | Touch the core SDK primitives in small examples |
| 02 | Handoffs Patterns | Compare handoffs and agents-as-tools |
| 03 | SandboxAgent Sampler | Show workspace, shell, skills, memory, and resumption |
| 04 | SQL Analyzer Agent | First full business reference solution |
| 05 | Realtime Voice Agent | Compare Python voice pipelines with browser realtime sessions |
| [06](lab-06-repl/lab-brief.md) | Interactive Agent REPL | Test conversation history and streaming in a terminal |
| [07](lab-07-vector-store/lab-brief.md) | OpenAI Vector Store | Build document Q&A with hosted retrieval, file citations, and resource cleanup |
| [08](lab-08-code-interpreter/lab-brief.md) | CSV to Diagram with Code Interpreter | Turn synthetic sales data into a downloadable chart using hosted Python execution |
| 10 | [Monitor Agent Runs in the OpenAI Dashboard](chapter-10/openai-dashboard-monitoring/lab-brief.md) | Connect two local mock MCP tools and group related agent traces with a shared `group_id` |
| 11 | [Visualize a Multi-Agent Handoff Architecture](chapter-10/multi-agent-architecture-visualization/lab-brief.md) | Draw two successive SDK handoffs and export a PNG with `openai-agents[viz]` |

## Reproducible Prompts

Use `prompts-index.md` to find the reusable Codex prompt pack for each lab. Each
reference solution includes a `BUILD-LOG.md` recording the prompt IDs and local
verification.

## Testing References

Use `reference-test-guide.md` for the two test layers:

- offline contract tests, which do not call OpenAI;
- OpenAI API smoke tests, which require `OPENAI_API_KEY` and can be forced with
  `REQUIRE_OPENAI_API=1`.

Use `run-reference-guide.md` when you want to try the references interactively
without running pytest.

## Recommended Build Order

1. Use Labs 00-03 before Lab 04 so you see Codex workflow, Agents SDK
   primitives, orchestration, and SandboxAgent concepts first.
2. Use Lab 04 as the first full business reference solution.
3. Use Lab 05 after you understand normal `Agent` objects; the voice lab
   reuses those objects in Python voice and browser realtime architectures.

Lab 06 is a short optional exercise you can take immediately after Lab 01.
Lab 07 also follows Lab 01 and teaches document ingestion, vector store search,
and `FileSearchTool` through a [guided reference](lab-07-vector-store/reference-solution/README.md).
Lab 08 follows Lab 01 and uses `CodeInterpreterTool` to create a PNG diagram
from a synthetic CSV, then [download and check the generated files](lab-08-code-interpreter/reference-solution/README.md).

Chapter 10 begins the chapter-based lab organization. Its first lab builds a
local MCP-backed agent and inspects grouped traces in the OpenAI dashboard.
Existing lab folders remain in their current locations pending the broader
chapter reorganization.

All labs now have a local `reference-solution/` folder inside their lab
directory.
