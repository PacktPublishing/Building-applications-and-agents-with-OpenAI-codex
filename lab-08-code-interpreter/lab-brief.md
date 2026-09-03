# Lab 08 — CSV to Diagram with Code Interpreter

**Status:** Reference implemented; 19 offline tests pass. Live chart generation
requires an API key and has not been run for this build.

**Time:** 25–35 minutes. **Prerequisite:** Lab 01 or familiarity with `Agent`
and `Runner.run`. Python 3.11+ and an OpenAI API key for the hosted exercise.

Give an agent a CSV containing 36 fictional sales records. The agent uses
OpenAI's hosted Code Interpreter to calculate monthly revenue and create a
PNG bar chart. Download the diagram and the CSV of plotted totals to your machine.

## What you will learn

- Supply a file to an explicit Code Interpreter container.
- Configure a real `Agent` with `CodeInterpreterTool` and run it with `Runner.run`.
- Let the model write and execute Python for aggregation and plotting.
- Inspect actual code calls, logs, file citation annotations, and token usage.
- Download container-generated files before the container expires or is deleted.
- Check the diagram's numbers and clean up the container and original upload.

## Start here

- [Codex build prompts](prompt-pack.md).
- [Reference setup and commands](reference-solution/README.md).
- [Guided learner exercise](reference-solution/lab-guide.md).
- [Synthetic CSV](reference-solution/data/sales.csv).
- [Build and verification record](reference-solution/BUILD-LOG.md).

The local generator only creates CSV data. All aggregation and chart creation
in the runnable demo happen through hosted Code Interpreter. No local plotting
code substitutes for the SDK agent flow.
