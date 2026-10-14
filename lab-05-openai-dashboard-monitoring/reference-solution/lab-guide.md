# Lab Guide: Dashboard Monitoring with a Local MCP Agent

The agent gets data from two local MCP tools. The weather fixture supports
five fixed cities, while the pool fixture contains a weekly schedule for the
fictional town Riverton. Both tool results say `mock data` so the agent can
clearly identify the synthetic source.

The runner makes two independent `Runner.run` calls. A trace represents one
run; `RunConfig.group_id` connects both traces under a shared conversation or
process identifier. The workflow name describes the app, and `trace_metadata`
adds searchable context to each trace.

After running, open Logs → Agents or Traces in the OpenAI dashboard. Review the
model generation and the corresponding MCP call span in each trace. Compare the
inputs and outputs against `mock_data.py`; then verify both traces carry the
same group ID and metadata.

## Exercises

1. Ask for weather in another supported city and compare the MCP arguments and
   result span.
2. Change the pool weekday to Friday. How does the tool output differ?
3. Change the shared `GROUP_ID` and rerun. How would you distinguish the new
   trace group from the previous group?
4. Propose one operational metric you could monitor from trace data, such as
   tool failure rate or run duration.
