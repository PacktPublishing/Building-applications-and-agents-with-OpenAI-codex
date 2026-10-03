# OpenAI Agents Labs Replay Environment

This folder is the clean build space for replaying the lab prompts with Codex.
It intentionally contains reusable context, not finished reference solutions.

## Included Context

- `AGENTS.md`: course implementation rules for Codex.
- `.agents/skills/openai-agents-sdk/`: repo-local SDK Skill.
- `.agents/skills/openai-agents-sdk/openai-agents-python/`: submodule pointing
  to the official `openai/openai-agents-python` repository for examples, tests,
  and docs.
- `labs/*/prompt-pack.md`: prompt packs for Labs 01-08 and Chapter 10 Labs 10-11.
- [Lab 06 REPL prompt pack](labs/lab-06-repl/prompt-pack.md): a short shopping-list exercise after Lab 01.
- [Lab 07 vector store prompt pack](labs/lab-07-vector-store/prompt-pack.md): document ingestion, hosted search, citations, and cleanup after Lab 01.
- [Lab 08 Code Interpreter prompt pack](labs/lab-08-code-interpreter/prompt-pack.md): a synthetic CSV becomes a downloadable diagram through hosted Python execution.
- [Chapter 10 Lab 10 monitoring prompt pack](labs/openai-dashboard-monitoring/prompt-pack.md): a local MCP-backed agent creates grouped traces for dashboard inspection.
- [Chapter 10 Lab 11 visualization prompt pack](labs/multi-agent-architecture-visualization/prompt-pack.md): three SDK Agents, two handovers, and PNG export through the `viz` extension.

## SDK Submodule

Before replaying labs, make sure the SDK submodule has been initialized from
the repository root:

```bash
git submodule update --init --recursive
```

The course pins the submodule to a specific commit so examples and tests remain
reproducible. To refresh it intentionally:

```bash
git submodule update --remote replay-environment/.agents/skills/openai-agents-sdk/openai-agents-python
```

After updating the SDK pin, rerun the local lab tests before sharing changes.

## How To Use

Start a new Codex task from this `replay-environment` folder and use one lab
prompt pack at a time.

Example for Lab 05:

```text
Use labs/lab-05-realtime-voice-agent/prompt-pack.md.
Follow the prompts in order.
Create the implementation in solutions/lab-05-realtime-voice-agent.
Do not inspect or copy from any reference-solution folder outside this replay
environment.
Use AGENTS.md, the openai-agents-sdk Skill, and the skill-local
openai-agents-python checkout as references.
```

## Replay Rules

- Build into `solutions/<lab-name>/`.
- Do not copy a finished `reference-solution/`.
- Use direct OpenAI Agents SDK objects.
- Keep SDK objects visible in code and tests.
- Make API-backed demos skip cleanly when `OPENAI_API_KEY` is absent.
- Record what prompt steps were used in the generated solution's `BUILD-LOG.md`.
