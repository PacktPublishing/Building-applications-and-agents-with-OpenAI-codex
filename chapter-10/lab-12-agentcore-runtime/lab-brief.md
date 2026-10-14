# Chapter 10 · Lab 12: Deploy an OpenAI Agent on AgentCore Runtime

Build one OpenAI Agents SDK `Agent`, deploy it on Amazon Bedrock AgentCore
Runtime, and inspect its agent, model, and function-tool spans in CloudWatch.

The agent answers questions about a small fictional course catalog. Its
`get_course_info` tool returns deterministic, explicitly synthetic data.
OpenAI supplies model inference; AgentCore supplies hosting and runtime sessions.

Students use the AgentCore CLI's Python CodeZip deployment, keep the OpenAI
key in Secrets Manager, and invoke with the CLI's SigV4-authenticated client.
The `opentelemetry-instrumentation-openai-agents` library converts SDK tracing
callbacks to OpenTelemetry spans. ADOT exports telemetry using AgentCore's
managed configuration; CLI deployment attempts Transaction Search setup.

Prerequisites: Lab 01, basic IAM knowledge, Python 3.12, Node.js 20+, `uv`,
AWS CLI v2, `@aws/agentcore@0.31.1`, an AWS account with AgentCore in the
chosen Region, and an OpenAI key with model access. Allow 45–60 minutes.
Deployment and invocation incur AWS and OpenAI usage charges.

Status: reference implementation built and locally verified. Live deployment
and CloudWatch ingestion remain learner/instructor validation steps.

Completion checkpoint: a deployed invocation returns a synthetic answer and
tool output; its returned OTEL trace ID leads to `invoke_agent`, `chat`, and
`execute_tool` spans in CloudWatch; two requests share the runtime session ID;
lab-specific cloud resources are cleaned up.

Use the [reference runbook](reference-solution/README.md), follow the
[exercises](reference-solution/exercises.md), or rebuild from the complete
[prompt pack](prompt-pack.md).
