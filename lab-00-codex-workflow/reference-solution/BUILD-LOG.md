# Build Log: Lab 00

## Prompts Used

- Prompt 1: create the `text-stats` CLI, tests, and README.
- Prompt 2: add project `AGENTS.md` guidance.
- Prompt 3: expose and fix a normalization bug through a failing test.

## Verification

- Local tests cover punctuation, empty input, and repeated words.
- This lab intentionally does not use the OpenAI Agents SDK.

## SDK 0.23.1 update

- Raised the OpenAI Agents SDK floor to `openai-agents>=0.23.1` (resolved
  0.23.1 with `openai` 3.31.0). Offline tests pass; live API tests were not rerun.
