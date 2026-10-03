# Lab 08 reference — CSV to Diagram

An SDK agent uses hosted Code Interpreter to turn a synthetic sales CSV into
a monthly revenue diagram. The reference downloads the PNG and the plotted
totals, then cleans up the temporary remote resources.

## Setup

From this `reference-solution/` directory, use Python 3.11+:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Verified versions: `openai-agents==0.17.2`, `openai==2.36.0`.
If you already ran the repository's `uv sync --frozen`, you can instead use
`../../.venv/bin/python` wherever the commands below say `python`.

Supply `OPENAI_API_KEY` through your environment or secret manager. The runner
does not load `.env` automatically. The agent explicitly uses `gpt-6-luna`, which supports Responses Code Interpreter. No local pandas or matplotlib installation is required:
the model runs that analysis code in the hosted container.

## Generate the diagram

The synthetic CSV is already included, so run:

```bash
python run_reference.py run
```

The command uploads `data/sales.csv`, creates a 1 GB container, runs the agent,
downloads generated files to a fresh `outputs/run-*/` folder, and attempts
remote cleanup. It prints the exact local paths:

```text
outputs/run-<unique-id>/
  monthly_revenue.png   # Downloaded Code Interpreter diagram
  monthly_totals.csv    # Downloaded data used for the plot
  run-report.json      # Actual tool calls, code, messages/citations, usage
```

Open `monthly_revenue.png` in your image viewer. The intended result is a bar
chart with twelve months of revenue, EUR labels, a zero baseline, and a title
identifying synthetic data. Confirm the diagram with the
[guided checks](lab-guide.md#4-check-the-diagram-and-its-numbers).

Without a nonblank API key, `run` and `cleanup` print `SKIP` and return success
without creating a client, output folder, or chart. Help also needs no key:

```bash
python run_reference.py --help
python run_reference.py run --help
```

## Input data and custom runs

[data/sales.csv](data/sales.csv) contains 12 months × 3 product categories for
the fictional Northstar Market. Regenerate the exact CSV locally with:

```bash
python generate_data.py
```

The generator produces input data only. To try another compatible synthetic CSV:

```bash
python run_reference.py run --csv /absolute/path/to/sales.csv --output-dir /tmp/sales-diagrams
```

The CSV must be UTF-8 (an optional BOM is accepted), nonempty, and include:

| Column | Meaning |
|---|---|
| `month` | Calendar month in `YYYY-MM` format. |
| `category` | Nonblank product category. |
| `orders` | Nonnegative integer order count. |
| `revenue_eur` | Finite, nonnegative revenue in EUR, using a decimal point. |

Each row's revenue is already a total for that row; the agent sums revenue
across categories for each month. It must not multiply revenue by orders again.
The template labels the diagram as synthetic.

## How the SDK is used

`run_reference.py` keeps `Agent`, `CodeInterpreterTool`, `ModelSettings`,
`Runner.run`, and `RunConfig` visible. `AsyncOpenAI.files.create` uploads the
CSV; `containers.create(file_ids=[...])` copies it into an explicit container.
The tool receives that container ID. The model writes and executes the Python
analysis and plotting code; the local runner neither executes model-generated
Python nor generates a fallback image.

`artifacts.py` extracts real `container_file_citation` annotations and downloads
their bytes with `client.containers.files.content.retrieve`. The local output
names are fixed, so a model-provided filename cannot choose another write path.
Missing/ambiguous citations or invalid downloaded data cause a visible failure.

See [official-source verification](docs/openai-docs-verification.md).

## Cleanup and recovery

Each run records its original upload and container in `resources.json` inside
its output folder. The runner attempts deletion in `finally`, including after
model/download failures. Successful cleanup removes that manifest and preserves
local artifacts. If cleanup fails, keep the manifest and retry:

```bash
python run_reference.py cleanup --run-dir "outputs/run-<unique-id>"
```

Replace the placeholder with the actual printed run directory. Cleanup deletes
only the recorded container and original Files API upload. Container deletion
also removes its generated files, which is why downloads happen first.

The container has a 20-minute inactivity expiration policy. Downloaded files
remain local; files left only in an expired container cannot be recovered.
Expiration does not replace deleting the original Files API upload.

Live runs can incur container and model charges. Token usage is not a complete
dollar bill; consult current [Code Interpreter pricing](https://developers.openai.com/api/docs/pricing#built-in-tools).

## Verification

Run the offline suite:

```bash
python -m unittest discover -s tests -v
```

The live test is skipped even when a key exists unless explicitly enabled:

```bash
RUN_CODE_INTERPRETER_SMOKE=1 REQUIRE_OPENAI_API=1 python -m unittest discover -s tests -p test_openai_integration.py -v
```

The live test retains its generated chart for review, checks a completed Code
Interpreter call, PNG header/dimensions, all twelve calculated totals against
independent Decimal arithmetic, and successful cleanup. `REQUIRE_OPENAI_API=1`
turns missing credentials into a failure when the live test is requested.

This build passed **19 offline tests**. The live test skipped because no API key
was available; no live-generated diagram is included. Offline tests establish
local behavior and SDK contracts. Visual correctness still requires opening
the actual chart after a live run.
