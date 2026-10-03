# Lab 06 reference: Shopping-list REPL

This tiny example uses `Agent` and `run_demo_loop` directly. It lets you test
conversation history and streaming from a terminal.

## Setup

Use Python 3.11+ and run these commands from this `reference-solution/`
directory (or your generated solution directory):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Supply `OPENAI_API_KEY` through your shell environment or secret manager.
The demo does not load `.env` automatically. Do not put a real key in source
files or commit it. Live conversations use the OpenAI API.

The agent explicitly uses `gpt-6-luna`.

```bash
python run_reference.py
python run_reference.py --no-stream
```

Run one command at a time. Without a nonblank API key, either command prints
a skip message and exits successfully. `python run_reference.py --help`
works without credentials.

If using the existing repository environment, no separate install is needed:
from the repository root run
` .venv/bin/python lab-06-repl/reference-solution/run_reference.py`.

## Manual test

Enter these messages one at a time in the running REPL:

```text
Add milk, eggs, and bread.
Remove eggs.
Add apples.
What is on my list?
quit
```

Expect the final list to contain milk, bread, and apples, with no eggs.
Wording and ordering may vary. Restart and ask “What is on my list?”; expect
an empty list. Repeat with `--no-stream` to see complete replies instead of
incremental text. `exit`, `quit`, or Ctrl-D ends the loop.

## What the SDK handles

`build_agent()` returns a real SDK `Agent`. `main()` calls the SDK's
`run_demo_loop(agent, stream=...)`, which reads terminal input and invokes
`Runner.run_streamed` or `Runner.run` internally. It carries the result's
input/output history into the next turn. This is in-memory conversation
history, not durable storage or a deterministic shopping database.

The verified SDK version is `openai-agents==0.17.2`. Its REPL helper does not
accept `run_config` or `session`. For custom tracing metadata, durable sessions,
or programmatic inspection of results, a separate direct `Runner` example
is a next step; it is not needed for this exercise.

## Offline verification

From this solution directory:

```bash
python -m unittest discover -s tests -v
```

The tests check SDK object construction, model selection, stream forwarding,
and the missing-key path. They mock only the application's call into the REPL
helper and make no model calls. They do not prove the model maintains the list.

- [ ] Offline tests pass.
- [ ] Live list-edit exercise produces the expected items.
- [ ] Both streaming modes work interactively.
- [ ] Restarting clears the conversation.

See [BUILD-LOG.md](BUILD-LOG.md) for actual verification status and the
[official SDK REPL documentation](https://openai.github.io/openai-agents-python/repl/)
for the helper's behavior.
