# Lab 06: Interactive Agent REPL

**Status:** Reference built; offline checks pass; live model exercise not yet verified.

**Time:** 20–30 minutes. **Prerequisite:** Basic Python and a first SDK `Agent`
(Lab 01). This lab can be taken immediately after Lab 01; Labs 02–05 are not required.

## Goal

Build a terminal shopping-list assistant and test it across multiple messages.
REPL means **read–eval–print loop**: read a message, run the agent, print its
reply, and repeat. Here, you enter natural-language messages, not Python code.

## What you build

A small Python program using `Agent` and the SDK's `run_demo_loop`, with
streaming on by default and a `--no-stream` option. The list is represented in
conversation history. There are no tools or database in this introductory lab.

By the end, you should be able to:

- Launch an interactive agent without writing a custom input loop.
- Demonstrate that a follow-up message uses earlier turns.
- Compare streamed text with a complete reply printed at once.
- Explain why exiting and restarting loses the previous conversation.
- Distinguish offline application checks from a live model behavior test.

## Build with Codex

Open `replay-environment/` in Codex. Paste:

```text
Use labs/lab-06-repl/prompt-pack.md and the openai-agents-sdk skill.
Follow REPL-01 through REPL-04 in order.
Build into solutions/lab-06-repl/.
Do not inspect or copy any reference-solution folder.
Record each prompt and actual verification in BUILD-LOG.md.
```

Alternatively, send the four prompts from [the prompt pack](prompt-pack.md)
one at a time. Inspect each diff and verification result before proceeding.
To try the finished version, follow the [reference runbook](reference-solution/README.md).

## Exercise 1 — Build a list across turns

Start the program and enter each message separately:

| Input | Expected list after the reply |
|---|---|
| Add milk, eggs, and bread. | milk, eggs, bread |
| Remove eggs. | milk, bread |
| Add apples. | milk, bread, apples |
| What is on my list? | milk, bread, apples |

Check membership rather than exact wording or order. The fourth message does
not repeat the list: it tests whether earlier turns are available to the agent.

## Exercise 2 — Watch streaming

Exit with `quit`. Restart with `--no-stream` and repeat the messages. A reply
now appears as a complete answer instead of text arriving incrementally.
Short replies can make streaming subtle; optionally ask for a paragraph
explaining how to organize the items in a grocery store.

The SDK helper uses `Runner.run_streamed` for streaming and `Runner.run` for
non-streaming. After each completed run it carries forward `to_input_list()`.
It also tracks `last_agent`, although this lab uses only one agent.

## Exercise 3 — Observe the history boundary

Type `exit`, restart, and ask “What is on my list?” before adding anything.
Expect an empty list. The earlier items were in the previous loop's memory;
they were not saved to a file or a session database.

This is model-maintained conversational state. Reliable application inventory
would require explicit data storage and tools, which are outside this lab.

## Acceptance checklist

- [ ] The entry point calls the SDK's `run_demo_loop` with a real `Agent`.
- [ ] The four-message exercise ends with milk, bread, and apples.
- [ ] `--no-stream` prints complete replies.
- [ ] `exit` and `quit` end the loop.
- [ ] A fresh process starts without the previous items.
- [ ] Missing credentials produce a clean skip without prompting.
- [ ] Offline tests pass, and the build log records whether live checks ran.

## Explain it back

1. What does `Agent` define, and what does `run_demo_loop` handle?
2. Why does “Remove eggs” work without repeating the entire list?
3. Why is this history different from persistent session storage?
4. Can a passing mocked test prove the model follows the list instructions?

Instructor key: agent behavior versus terminal orchestration; prior input and
output items are carried forward; loop memory ends on restart; mocked tests
verify application wiring, not live model behavior.

Reference: [Official SDK REPL guide](https://openai.github.io/openai-agents-python/repl/).
