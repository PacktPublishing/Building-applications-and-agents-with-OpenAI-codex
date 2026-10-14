# Build Log: Lab 04

## Prompts Used

- Prompt 1: handoff triage with billing and technical specialists.
- Prompt 2: result logging with `final_output` and `last_agent.name`.
- Prompt 3: agents-as-tools manager with `Agent.as_tool`, visible tool outputs,
  and `last_agent`.
- Prompt 4: trace comparison worksheet.
- Prompt 5: shared `RunConfig` and orchestration contract tests.

## Verification

- `uv run --with pytest pytest -q`: 5 passed.
- Tests validate real SDK handoffs, agents-as-tools, scenarios, and RunConfig.

## Model alignment update

- Set the text Agent/SandboxAgent default to `gpt-6-luna`; retained specialized voice and transcription models where applicable.
- Offline verification after the update: 6 passed, 2 skipped.

## SDK 0.23.1 update

- Raised the OpenAI Agents SDK floor to `openai-agents>=0.23.1` (resolved
  0.23.1 with `openai` 3.31.0). Offline tests pass; live API tests were not rerun.

## Renumbering — Lab 02 to Lab 04

- Renamed `lab-02-handoffs-patterns/` (temporarily `lab-002-handoffs-patterns/`)
  to `lab-04-handoffs-patterns/`, and the replay prompt pack folder to
  `replay-environment/labs/lab-04-handoffs-patterns/`.
- Updated titles, `workflow_name`, trace metadata, the contract test, prompt
  packs, and repository-level guides to Lab 04.
