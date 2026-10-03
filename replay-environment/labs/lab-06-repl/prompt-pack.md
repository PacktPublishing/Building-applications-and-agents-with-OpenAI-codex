# Prompt Pack: Lab 06 — Interactive REPL

Run REPL-01 through REPL-04 in order in the same Codex task. This pack is
self-contained; a replay must not read or copy any reference solution.
Use the repo-local openai-agents-sdk skill and official SDK checkout.

For a reference build, use `lab-06-repl/reference-solution/` as the output
directory. For a learner replay, work from `replay-environment/` and use
`solutions/lab-06-repl/`. Use that same output directory for every prompt.

## REPL-01 — Build the smallest interactive agent

```text
Build a small Python shopping-list REPL in the agreed output directory.
Read AGENTS.md and the openai-agents-sdk skill. Inspect the installed SDK and
the official checkout's src/agents/repl.py before choosing parameters.
Use a real Agent and the SDK's run_demo_loop imported from agents. Do not
write your own input loop or framework. Implement build_agent() and async
main() in run_reference.py, with an asyncio.run(main()) entry point.
Instruct the agent to add/remove shopping items, show the whole list after
each change, avoid inventing items, and say the list is empty when appropriate.
Keep state in conversation history only: no database, tools, or sessions.
Set the SDK Agent model explicitly to `gpt-6-luna`.
If OPENAI_API_KEY is missing or blank, print a clear skip message and return
before prompting or making a model call. Never print credentials.
Start BUILD-LOG.md and record REPL-01 and its verification honestly.
```

## REPL-02 — Compare streaming modes

```text
Add argparse support for --no-stream. Default to run_demo_loop(agent,
stream=True); use stream=False when the flag is supplied. Keep one call to
the real SDK helper. Print a short startup hint explaining exit and quit.
Do not pass run_config or session: the course SDK's run_demo_loop does not
expose those parameters. Explain in documentation that the SDK helper calls
Runner internally; students need not implement that loop.
Run --help and verify the no-key path in both modes. Record REPL-02 in
BUILD-LOG.md with commands and actual results.
```

## REPL-03 — Add offline contract checks

```text
Add tests/test_repl.py using unittest so tests can run without extra test
dependencies or API access. Verify build_agent returns a real SDK Agent and
uses the fixed `gpt-6-luna` model. Patch the application boundary run_demo_loop with
AsyncMock to verify main forwards a real Agent and the correct stream flag
in both modes. Use a dummy key only with that boundary mocked. Check that
an absent or whitespace-only key prints a skip message and never calls the
helper. Patch argv in CLI tests. Do not test exact model wording or reproduce
the SDK's internals. Run python -m unittest discover -s tests -v from the
output directory. Record results under REPL-03 in BUILD-LOG.md.
```

## REPL-04 — Write the learner runbook

```text
Write README.md and requirements.txt. Pin openai-agents to the version
actually verified for this build. Document Python 3.11+, isolated venv setup,
dependency installation, OPENAI_API_KEY through the environment (no committed
secret), fixed `gpt-6-luna` model, launch commands, offline tests, and --no-stream.
Include a manual exercise: add milk/eggs/bread, remove eggs, add apples, ask
for the list, exit, restart, and ask for the list again. Expected first result:
milk, bread, apples; after restart: no previous items. Explain conversation
history is in memory, not durable storage or a deterministic shopping database.
Include an acceptance checklist and distinguish offline verification from
live model behavior. Do not claim a live run unless one was performed.
Link the official SDK REPL docs. Record REPL-04 and final checks in BUILD-LOG.md.
```
