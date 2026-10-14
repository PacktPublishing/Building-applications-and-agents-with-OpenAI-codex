# Lab 12 exercises

1. Run the offline tests. Read `agent.py`, `runtime_app.py`, and `telemetry.py`.
   Point to the actual `Agent`, function tool, `Runner.run`, and OTEL registration.
   Explain why disabling SDK tracing would hide framework spans.
2. Run the local HTTP server with ADOT console export. Send a course question,
   find its tool output, and match the returned trace ID to console spans.
   Send a blank prompt; confirm a 400 response before a model call.
3. Create the dedicated secret and prepare the CLI project. Inspect its
   runtime configuration and scoped IAM policy. Run `agentcore package`,
   then `agentcore deploy` and `agentcore status`. Check for Transaction Search
   setup warnings. Explain the deployer, runtime role, and caller permissions.
4. Invoke two course questions with `agentcore invoke` and one session ID.
   Capture the JSON responses. Use `agentcore traces list` and `traces get`
   plus the CloudWatch console to locate agent, model, and tool operations.
   Compare tokens and duration. Explain why a shared runtime session does
   not imply conversation memory.
5. Change one synthetic catalog sentence in the original `agent.py`, rerun
   preparation, and run `agentcore deploy` again. Use a fresh session ID to
   verify the new tool output and CloudWatch trace.
6. Clean up with `agentcore remove all` followed by `agentcore deploy`.
   Confirm cloud teardown, schedule deletion of the dedicated secret, and
   remove a retained lab log group if present. Preserve shared settings.

Completion evidence: passing offline tests, successful CLI package/deployment,
two responses with synthetic tool data, CloudWatch framework spans matching
the returned IDs, and cleanup confirmation. A successful answer by itself
does not establish that telemetry reached CloudWatch.
