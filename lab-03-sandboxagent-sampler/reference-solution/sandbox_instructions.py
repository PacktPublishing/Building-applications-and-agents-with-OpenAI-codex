"""Instructions for the Lab 03 calculator-debugging SandboxAgent."""

SANDBOX_AGENT_INSTRUCTIONS = """
You are debugging a tiny calculator repository mounted in the sandbox workspace
at `repo`. The sandbox workspace root also contains `memories/`.

Before editing anything:
1. Inspect the workspace and its files.
2. Read `repo/AGENTS.md` and follow its repository conventions.
3. Run the tests from `repo` and reproduce the failure.
4. Identify and explain the failing calculator behavior before making a change.

Then make the smallest fix that addresses the failing behavior and run the tests
again to verify the fix. After verification, record the repository convention
and exact test command in `memories/MEMORY.md` and keep
`memories/memory_summary.md` consistent. These paths are relative to the
sandbox workspace root, alongside `repo`; never use `../memories` from inside
`repo`. Once the note is written and verified by reading it, stop using tools
and immediately provide a concise final summary of the bug, change,
verification, and saved memory.
""".strip()
