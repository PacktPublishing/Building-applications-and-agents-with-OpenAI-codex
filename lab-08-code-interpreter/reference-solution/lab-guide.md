# Lab 08 — Turn a CSV into a diagram

Allow 25–35 minutes after [setup](README.md#setup). Run the commands from this
solution directory, using the Python environment from the README.

## 1. Inspect the synthetic dataset

Open [data/sales.csv](data/sales.csv). It contains 36 rows: three product
categories for every month of 2025. The first month's rows are:

```csv
month,category,orders,revenue_eur
2025-01,Grocery,120,2640.00
2025-01,Household,60,900.00
2025-01,Personal care,40,480.00
```

These are fictional Northstar Market sales. The figures follow deterministic
formulas in `generate_data.py`; there is no external dataset to fetch.
`revenue_eur` is the total for a row. For January, the plotted revenue should
be **2640 + 900 + 480 = EUR 4020.00**.

## 2. Follow the file into Code Interpreter

Read `run_reference.py`, starting at `main()`:

1. Validate the CSV schema locally.
2. Upload the file with `client.files.create(..., purpose="user_data")`.
3. Create a hosted container with `client.containers.create(file_ids=[uploaded.id])`.
4. Attach that container to a real SDK `CodeInterpreterTool`.
5. Execute the agent with `Runner.run` and a `RunConfig`.

The core configuration is:

```python
agent = Agent(
    name="sales_chart_analyst",
    instructions="Use the python tool to read the CSV, aggregate revenue, and save a chart.",
    tools=[CodeInterpreterTool(tool_config={
        "type": "code_interpreter",
        "container": container_id,
    })],
    model_settings=ModelSettings(
        tool_choice="required",
        response_include=["code_interpreter_call.outputs"],
    ),
)
```

The full instructions in `build_agent()` specify the chart and totals file.
The model chooses and executes Python code for the analysis. Local validation
only checks the input structure; it does not aggregate or plot the data.

An explicit container lets the runner record its ID before the model executes
and clean it up even if execution fails. Auto containers are also supported;
compare the two modes in the official
[Code Interpreter guide](https://developers.openai.com/api/docs/guides/tools-code-interpreter).

## 3. Run the agent and download its files

```bash
python run_reference.py run
```

Expect progress messages for the upload and container creation. The model run
can take a minute or more. The runner prints its answer, actual Code Interpreter
call statuses, generated Python code/logs when returned, token usage, download
paths, and cleanup messages. It bounds the model run at five minutes.

The intended diagram is a 1600×900 PNG bar chart with one bar per month, teal
bars on white, a synthetic-data title, labeled axes, and revenue in EUR.
The model also saves the totals used in the chart to `monthly_totals.csv`.

Read `artifacts.py`. It retrieves these files from real
`container_file_citation` annotations in `result.new_items`, using the returned
container and file IDs. A `cfile_...` ID belongs to a container; it is downloaded
with the container file content endpoint, not `client.files.content`.
A `sandbox:/mnt/data/...` link in model prose alone is not enough.

Both files are downloaded before the temporary container is deleted. See the
official guidance on [working with generated files](https://developers.openai.com/api/docs/guides/tools-code-interpreter#work-with-files).

## 4. Check the diagram and its numbers

Open the printed `monthly_revenue.png` path and inspect `monthly_totals.csv`.

- There should be twelve bars, January through December, in chronological order.
- The y-axis should begin at zero and identify EUR. The title should identify
  synthetic monthly revenue. Month names and value labels should be readable.
- January should show **EUR 4020.00**; December should show **EUR 8702.00**.
- The graph should dip in February, June, and July relative to the previous
  month, then rise from August through December. December should be highest.
- The graph must sum all three categories, not average them, plot only Grocery,
  or multiply row revenue by order count.

The live smoke test checks the totals using independent arithmetic. PNG header
checks cannot prove that bar heights match the CSV or that labels are unclipped;
you must still inspect the diagram visually. The model can make mistakes even
when Python executes successfully.

## 5. Inspect execution and tracing

Open `run-report.json`. Find:

- A `code_interpreter_calls` item with `status: "completed"` and the recorded
  container ID.
- Python code that reads the CSV, groups `revenue_eur` by month, sorts the
  months, and writes the PNG and totals CSV.
- `container_file_citation` annotations in `output_messages` for both files.
- The row count and token usage.

Ask yourself: what would happen if you only printed `final_output`? You would
have the answer and temporary links but would not have downloaded the files.

`RunConfig` names the workflow `lab-08-code-interpreter` and sets lab metadata.
When tracing is available to your API project, find that workflow in the trace
viewer. `trace_include_sensitive_data=False` limits sensitive payloads in
traces; the input CSV and analysis still go to OpenAI, and this lab deliberately
saves generated code/logs and messages in the local report.

## 6. Change the input and compare diagrams

Copy `data/sales.csv` to another CSV and change one value: set January Grocery
revenue from `2640.00` to `3640.00`. Then run:

```bash
python run_reference.py run --csv /absolute/path/to/modified-sales.csv
```

The new January total should be **EUR 5020.00**, with all other months unchanged.
Each run uses a fresh output folder, so you can compare both diagrams. This
checks that the agent is reading the supplied file rather than relying on a
hard-coded example. You can also change `build_agent()` to request a line chart;
keep the PNG filename and the totals CSV contract the same.

## 7. Confirm cleanup

A successful run removes the container and original uploaded CSV. It removes
`resources.json` only after cleanup succeeds and leaves the downloaded files
and report in place. If the manifest remains, fix API access/connectivity and run:

```bash
python run_reference.py cleanup --run-dir "outputs/run-<unique-id>"
```

Use the actual printed folder name. Do not delete the manifest to clear an
error. If a creation response was lost, the manifest cannot know that resource
ID; inspect the printed IDs and the lab-named container in your API project.
Containers are temporary, so a failed download requires a fresh run after the
container is deleted or expires.

## Troubleshooting

| Symptom | What to check |
|---|---|
| `SKIP` and no chart | Set a nonblank `OPENAI_API_KEY` in this shell; no hosted execution occurred. |
| Invalid CSV | Use the documented schema, ISO months, numeric orders/revenue, and UTF-8 encoding. |
| Authentication/model error | Check project access to `gpt-6-luna`; API error bodies are suppressed to avoid echoing key fragments. |
| No completed code call | Inspect the report, model capability, and tool configuration. |
| Missing or ambiguous cited files | Inspect output messages. The final answer must link one generated PNG and one totals CSV. |
| Invalid PNG or totals | Inspect generated code and rerun after correcting the instructions/input. No local fallback image is produced. |
| Timeout or expired container | Start a fresh run. Files left only in an expired container cannot be recovered. |
| Cleanup failure | Retain `resources.json` and retry cleanup for that run directory. |

## Acceptance checklist

- [ ] The agent executes Python through hosted Code Interpreter.
- [ ] The uploaded CSV, not a locally generated chart, supplies the plotted data.
- [ ] A PNG diagram and totals CSV are downloaded using actual file citations.
- [ ] The twelve monthly totals match the synthetic data.
- [ ] The chart's axes, labels, bar heights, and synthetic-data title are correct.
- [ ] Changing January's input revenue changes January's plotted total.
- [ ] Temporary remote resources are cleaned up; local artifacts remain.
- [ ] Offline and live verification are recorded separately.
