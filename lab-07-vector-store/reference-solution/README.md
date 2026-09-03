# Lab 07 reference — OpenAI Vector Store

Create a searchable document knowledge base and query it through the OpenAI
Agents SDK. The reference contains three fictional Northstar Market policies,
a resource lifecycle module, a four-command runner, and offline tests.

## Setup

From this `reference-solution/` directory, use Python 3.11+:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The verified dependencies are `openai-agents==0.17.2` and `openai==2.36.0`.
Alternatively, after the repository's `uv sync --frozen`, replace `python`
in the commands below with `../../.venv/bin/python`; no separate install is
needed with the existing locked workspace environment.

Supply `OPENAI_API_KEY` through your environment or secret manager. The demo
does not load `.env` automatically. Set `OPENAI_MODEL` to override the SDK's
default model with a model available to your project that supports file search.
The runner uses the Responses API through the SDK's `OpenAIProvider`.

## Run the lab

Run these commands one at a time from this directory:

```bash
python run_reference.py ingest
python run_reference.py search "Can I return unopened coffee after 10 days?"
python run_reference.py ask "Can I return unopened coffee after 10 days, and when do next-day orders close?"
python run_reference.py search "returns" --category returns --max-results 2
python run_reference.py ask "What was Northstar Market's annual revenue?"
python run_reference.py cleanup
```

Without a nonblank API key, every command prints `SKIP` and exits successfully
without creating a client or changing resources. `--help` works without a key.

| Command | What happens |
|---|---|
| `ingest` | Creates a store, uploads the three files, waits for each to finish indexing, and records resource IDs. |
| `search` | Calls `client.vector_stores.search` and prints filenames, scores, and passages. No generated answer. |
| `ask` | Calls `Runner.run` with a real `Agent` and `FileSearchTool`; prints the answer, tool results, actual citations, and token usage. |
| `cleanup` | Deletes the recorded store and uploaded Files API objects, then removes the manifest. |

Use the [lab guide](lab-guide.md) for exercises, expected facts, and troubleshooting.

## State and cleanup

The default `.vector-store-state.json` lives beside `run_reference.py` and is
ignored by git. It contains only a schema version, store ID, file IDs, and
indexing readiness. Keep it until cleanup succeeds. Repeated `ingest` is
rejected to prevent losing track of existing resources; `search` and `ask`
reuse the same store.

For a separate run, select a different manifest before the subcommand:

```bash
python run_reference.py --state /tmp/northstar-lab.json ingest
python run_reference.py --state /tmp/northstar-lab.json ask "What are the support hours?"
python run_reference.py --state /tmp/northstar-lab.json cleanup
```

Use one process per manifest. Do not edit its IDs or reuse its uploaded files in
another store: cleanup deletes those Files API objects. Partial ingestion and
cleanup failures preserve known resource IDs so cleanup can be retried. A store
expires one day after its last activity as a fallback, but expiration does not
replace cleanup of the original uploaded files.

Live runs can incur storage, hosted tool, and model charges. Token usage printed
by `ask` is not a total dollar bill and does not measure storage. Review current
[API pricing](https://developers.openai.com/api/docs/pricing) before live use.

## Verification

All offline tests run without credentials or model calls:

```bash
python -m unittest discover -s tests -v
```

The live smoke test skips by default, even when a key exists. To opt in:

```bash
RUN_VECTOR_STORE_SMOKE=1 REQUIRE_OPENAI_API=1 python -m unittest discover -s tests -p test_openai_integration.py -v
```

It uploads the bundled fictional documents, verifies filtered search and an
agent answer with real file citations, and cleans up in `finally`. If cleanup
fails, it prints the retained manifest path for recovery. `REQUIRE_OPENAI_API=1`
turns missing credentials into a failure when the live test is requested.

This build passed **23 offline tests**; the live smoke test was skipped because
no API key was available. Offline tests establish SDK object contracts and local
resource handling, not the quality of hosted retrieval or model answers.

## Files to read

- [run_reference.py](run_reference.py): `build_agent`, `build_run_config`, CLI,
  `Runner.run`, returned search items, file annotations, and usage.
- [store.py](store.py): direct `AsyncOpenAI` upload/index/delete calls and state.
- [data/returns.md](data/returns.md), [data/delivery.md](data/delivery.md), and
  [data/support.md](data/support.md): facts to check against the answer.
- [Official-source verification](docs/openai-docs-verification.md).
- [BUILD-LOG.md](BUILD-LOG.md): ordered prompt steps and actual verification.
