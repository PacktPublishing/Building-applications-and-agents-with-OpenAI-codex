# Lab 08: SandboxAgent Sampler

This lab uses the OpenAI Agents SDK `SandboxAgent` to inspect and repair a
small calculator repository mounted into a Unix-local sandbox. The manifest
mounts the calculator at relative path `repo` and seeded file memory at the
sandbox root under `memories/`.

## Run the deterministic checks

From this folder, uv installs the dependencies declared in `pyproject.toml`
into the repository's workspace environment:

```sh
uv run --extra dev pytest -q
uv run python check_manifest.py
```

The checks construct SDK objects and validate the relative manifest. They do
not make model calls.

## Run the sandbox repair demo

Set `OPENAI_API_KEY`, then run:

```sh
uv run python run_sandbox_demo.py
```

The streamed demo prints model and tool progress. It snapshots the Unix-local
workspace, closes the session so SDK memory generation can flush, exports the
workspace to `artifacts/latest-workspace/`, and then removes the temporary
sandbox directory. Use `--no-stream` for the `Runner.run` path and
`--max-turns` to change the turn limit.

## Explore persistent memory

`memory-resumption-worksheet.md` describes the two-run exercise. Run it with:

```sh
uv run python run_memory_demo.py
```

It creates one snapshot for both runs and exports the final workspace to
`artifacts/memory-demo-workspace/`. Inspect generated memory with:

```sh
find artifacts/memory-demo-workspace/memories -type f
cat artifacts/memory-demo-workspace/memories/MEMORY.md
```

Unix-local workspaces are temporary. The demos export them before deletion so
their files can be inspected afterward.
