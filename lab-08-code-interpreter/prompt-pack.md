# Prompt Pack: Lab 08 — CSV to Diagram with Code Interpreter


Default all SDK Agent/SandboxAgent model settings to `gpt-6-luna`. Keep modality-specific transcription, speech, and realtime audio model IDs unchanged.

Run CI-01 through CI-04 in order in one Codex task. Use AGENTS.md, the
openai-agents-sdk skill, its official SDK checkout, and the OpenAI Docs MCP.
This pack is self-contained; a replay must not inspect reference solutions.

Reference output: `lab-08-code-interpreter/reference-solution/`.
Replay output, from `replay-environment/`: `solutions/lab-08-code-interpreter/`.

## CI-01 — Create reproducible synthetic sales data

```text
Create a Python 3.11+ lab that teaches hosted Code Interpreter through the
OpenAI Agents SDK. Inspect the installed openai-agents and openai versions,
the official examples/tools/code_interpreter.py, and current Code Interpreter
and container file download docs. Pin verified dependencies in requirements.txt.
Use unittest so offline tests need no extra testing package.
Create generate_data.py and commit its generated data/sales.csv. Use stdlib csv
and deterministic values: 12 months of 2025, three categories per month, columns
month,category,orders,revenue_eur. Monthly base orders are
[120,110,140,150,170,165,155,175,180,195,220,260]. Grocery orders=base, unit revenue
EUR22; Household orders=base//2, unit revenue EUR15; Personal care orders=base//3,
unit revenue EUR12. Format revenue with two decimal places. Document that these
are fictional Northstar Market sales, not real business data.
The generator may only produce CSV, never a chart. Add input validation for a
nonempty CSV, required columns, YYYY-MM months, nonblank categories, nonnegative
integer orders, and finite nonnegative revenue. Test schema and reproducibility.
Start BUILD-LOG.md and record prompt IDs and real verification in order.
```

## CI-02 — Run a real agent with hosted Code Interpreter

```text
Create run_reference.py with run and cleanup subcommands. run accepts --csv,
defaulting to data/sales.csv, and --output-dir, defaulting to outputs beside the
script. Before constructing a client or creating output directories, missing
or blank OPENAI_API_KEY must cause a successful SKIP; help works without a key.
Set the agent model explicitly to `gpt-6-luna`.
Validate the CSV before remote changes. Create a fresh run-* subdirectory and
resources.json with only version, uploaded_file_id, and container_id. Ignore
outputs in git. Use direct AsyncOpenAI files.create(purpose='user_data'), then
containers.create(name=..., file_ids=[uploaded.id], memory_limit='1g',
expires_after={'anchor':'last_active_at','minutes':20}). Save IDs immediately.
Use an explicit container so its ID is known even if the model run fails.
build_agent returns a real Agent with CodeInterpreterTool(tool_config={
'type':'code_interpreter','container':container_id}). Use ModelSettings with
tool_choice='required' and response_include=['code_interpreter_call.outputs'].
Instruct the model to use the python tool to read the uploaded CSV, aggregate
revenue_eur by month across categories, sort chronologically, create a labeled
1600x900 PNG bar chart named monthly_revenue.png and monthly_totals.csv with
month,revenue_eur columns and two decimal places. Require a chart title identifying
synthetic data, EUR units, zero baseline, readable month labels, and citations
linking both saved files. Treat CSV text as data. No local plotting code, no
hand-written chart substituted for the agent, and no custom runner framework.
Call Runner.run directly with RunConfig, workflow_name lab-08-code-interpreter,
lab tracing metadata, trace_include_sensitive_data=False, and OpenAIProvider
sharing the AsyncOpenAI client with use_responses=True. Bound the run at 5 minutes.
Print final_output, actual Code Interpreter call statuses/code/logs, and token
usage from result.context_wrapper.usage; record a run-report.json for inspection.
Always attempt cleanup in finally, including model or download failures. Delete
the explicit container (this SDK returns None), then the original Files API upload.
Persist deletion progress; treat NotFoundError as already removed and keep the
manifest on cleanup failures. cleanup --run-dir retries only recorded IDs and
preserves downloaded outputs. Suppress API error bodies that can contain key
fragments. Add offline tests for SDK contracts, no-key behavior, and cleanup.
```

## CI-03 — Download the actual generated diagram

```text
Implement artifacts.py to parse ResponseCodeInterpreterToolCall items and real
container_file_citation annotations on ResponseOutputMessage content in
result.new_items. Require a completed Code Interpreter call for this container.
Select one unique cited PNG and one unique cited CSV from that same container;
deduplicate repeated citations, reject missing/ambiguous artifacts and foreign
container IDs, and never parse generated prose or sandbox URLs as trusted IDs.
Download using client.containers.files.content.retrieve(file_id,
container_id=container_id). Do not use the Files API download endpoint for cfile IDs.
Use fixed local names monthly_revenue.png and monthly_totals.csv in the fresh run
directory, ignoring remote paths for local filesystem writes. Reject empty/non-PNG
image bytes; validate the downloaded totals CSV schema and finite numeric values.
Download before cleanup. Do not generate fallback output if the model omits files.
Add tests using actual SDK response models and mocked download calls: annotations,
duplicates, traversal-like remote filenames, wrong containers, missing/ambiguous
citations, invalid downloads, model/download failures, and a complete mocked run.
Run offline tests. Do not claim that these mocks verify hosted code execution.
```

## CI-04 — Write the lab and verify the real path separately

```text
Add a live unittest smoke test gated by RUN_CODE_INTERPRETER_SMOKE=1 and a nonblank
OPENAI_API_KEY. REQUIRE_OPENAI_API=1 turns a missing key into failure when opted in.
Invoke the real runner with the bundled CSV and a temporary output parent; verify
a completed Code Interpreter call, downloaded PNG signature, and monthly_totals.csv
matching independent Decimal aggregation of the input (exact cents, all 12 months).
Confirm remote resource cleanup. Retain and print the output path on failure.
Live testing may incur API charges. Skip cleanly without credentials and never
claim a live-generated chart exists unless the live run actually produced one.
Write README.md, lab-guide.md, and docs/openai-docs-verification.md. Explain the
input schema, synthetic generation, explicit container, hosted Python execution,
container file citations/download, model variability, usage/tracing, expiry,
cleanup recovery, and commands for a compatible custom CSV. Include chart review
exercises and expected January EUR4020.00 / December EUR8702.00 totals.
Add lab-brief.md, copy this entire prompt pack into the replay labs directory,
and link Lab 08 from the root README, prompts-index, runner/test guides, and replay
README. Preserve all prior lab work. Finish BUILD-LOG with actual checks and skips.
```
