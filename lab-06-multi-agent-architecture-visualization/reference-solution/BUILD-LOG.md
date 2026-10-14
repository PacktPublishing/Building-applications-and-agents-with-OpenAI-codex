# Build Log

## Prompt steps

- Prompt 1: Created three SDK `Agent` objects with two sequential handoffs and
  set each agent's model to `gpt-6-luna`.
- Prompt 2: Added PNG export using `agents.extensions.visualization.draw_graph`
  from the `openai-agents[viz]` extra.
- Prompt 3: Added offline architecture, DOT-edge, and PNG-signature tests.
- Prompt 4: Added lab and replay navigation.

## Verification

- Installed the Python `openai-agents[viz]` extra and native Graphviz 16.1.0.
- `./.venv/bin/python -m pytest -q`: **3 passed**.
- `./.venv/bin/python export_diagram.py`: wrote
  `outputs/multi-agent-handoffs.png`; `file` identified a valid 162 × 523 PNG.
- Inspected the generated diagram: it shows the start node, all three agents,
  both directed handovers, and the end node.
- No model/API calls are needed for export or tests.

## SDK 0.23.1 update

- Raised the OpenAI Agents SDK floor to `openai-agents>=0.23.1` (resolved
  0.23.1 with `openai` 3.31.0). Offline tests pass; live API tests were not rerun.

## Renumbering — Chapter 10 to Lab 06

- Moved `chapter-10/multi-agent-architecture-visualization/` to `lab-06-multi-agent-architecture-visualization/`, and the replay prompt pack folder to
  `replay-environment/labs/lab-06-multi-agent-architecture-visualization/`.
- Updated titles, prompt packs, and repository-level guides to Lab 06.
