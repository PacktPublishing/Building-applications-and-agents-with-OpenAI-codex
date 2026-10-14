# Lab 03: Resume with file-based memory

## Goal

Practice carrying a useful repository convention from one SandboxAgent run to
the next using the SDK `Memory` capability and sandbox files.

## Run 1: Write a durable note

Run the SandboxAgent with the calculator workspace mounted as `repo`. Ask it to
read `repo/AGENTS.md`, then write a short durable note in
`memories/MEMORY.md` recording the source/test layout and the exact local test
command. Ask it to keep `memories/memory_summary.md` consistent with that note.
The memory files are at the sandbox workspace root, alongside `repo`; from
inside `repo`, do not address them through `../memories`. The note should
mention that fixes should be minimal and based on a reproduced failure.

## Run 2: Verify resumption

Close the first live session so the SDK can generate memory, then resume its
state with the same `UnixLocalSandboxClient` (`client.resume(sandbox.state)`).
Run the same SandboxAgent in that resumed session. Ask it to read both
`memories/MEMORY.md` and `memories/memory_summary.md`, then report the
repository convention and verification command it found. Confirm that it got
the facts from those files rather than guessing or re-reading the prior run.

## Inspect the generated memory

Generated sandbox memory normally lives under `memories/` in the active sandbox
workspace. Use the sandbox workspace path printed or observed during the run:

```bash
find <sandbox-root>/memories -maxdepth 2 -type f
cat <sandbox-root>/memories/MEMORY.md
cat <sandbox-root>/memories/memory_summary.md
```

Temporary UnixLocal sandbox workspaces may be deleted after cleanup, so the
stable seeded course artifact is this solution's local `memories/` folder.
The debugging demo exports its closed workspace to
`artifacts/latest-workspace/` before deleting the temporary UnixLocal
workspace. Inspect its generated memory after a run with:

```bash
find artifacts/latest-workspace/memories -maxdepth 2 -type f
cat artifacts/latest-workspace/memories/MEMORY.md
cat artifacts/latest-workspace/memories/memory_summary.md
```
