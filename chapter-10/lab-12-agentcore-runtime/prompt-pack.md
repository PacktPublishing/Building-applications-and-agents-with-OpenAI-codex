# Prompt Pack: Chapter 10, Lab 12

Follow L12-01 through L12-05 in order. Build into `reference-solution/` for the
course reference, or `solutions/lab-12-agentcore-runtime/` in the replay
environment. Do not inspect or copy reference solutions during replay.
Use AGENTS.md, the repo-local openai-agents-sdk Skill, its official SDK
checkout, OpenAI Docs MCP, and current official AWS documentation.

## L12-01 — One agent and one synthetic tool

```text
Create a Python 3.12 reference for deploying a simple OpenAI Agent on Amazon
Bedrock AgentCore Runtime. Define a real SDK Agent named course_assistant with
default model gpt-6-luna (override via OPENAI_MODEL). Give it one real
@function_tool get_course_info(topic), backed by a deterministic fictional
catalog with agents, deployment, and observability topics. Clearly label
every tool response as synthetic. Instructions must require the tool for
course questions. Expose build_agent() and build_run_config(session_id) that
return SDK objects. Keep Runner.run visible, limit the run to four turns, and
use a workflow name, trace metadata, and group_id equal to the runtime session
ID. Do not introduce a runner/framework layer. Add pinned requirements for
openai-agents, bedrock-agentcore, boto3, botocore[crt], pydantic, aws-opentelemetry-distro,
and opentelemetry-instrumentation-openai-agents; resolve a universal Python
3.12 requirements.lock for reproducible Linux ARM64 CodeZip builds. Keep this
environment independent of the older root course lockfile.
```

## L12-02 — Runtime contract, credentials, and instrumentation

```text
Use BedrockAgentCoreApp with an async @app.entrypoint handler and RequestContext.
Serve /ping and /invocations on 0.0.0.0:8080. Accept only a nonblank string
prompt of at most 2000 characters; reject extra fields and invalid payloads
before Runner.run. Return final_output, last_agent, tool_outputs, runtime
session ID, input/output token usage, and the 32-character OpenTelemetry trace
ID. Propagate session.id in OTEL baggage and detach it in finally. Wrap the
run in a current OTEL invocation span so SDK spans inherit its trace.
Load a local OPENAI_API_KEY or a Secrets Manager secret referenced by
OPENAI_API_KEY_SECRET_ARN with JSON field OPENAI_API_KEY. Read the secret once
at startup and pass the key to the SDK without logging it or putting it in
the deployment artifact. Use set_default_openai_key with use_for_tracing=False. Add a no-key
demo that skips before imports/network calls.
Use OpenAIAgentsInstrumentor(replace_existing_processors=True).instrument()
from opentelemetry.instrumentation.openai_agents. Keep SDK tracing enabled;
the instrumentor replaces the OpenAI dashboard exporter, not SDK callbacks.
ADOT owns the tracer provider/exporters. Disable automatic openai_agents
discovery only, since registration is explicit. Document these choices.
```

## L12-03 — AgentCore CLI deployment and invocation

```text
Use the current Node CLI @aws/agentcore, pinned to 0.31.1, for deployment.
Prefer Python CodeZip so learners need neither Docker nor manual ECR or
CloudFormation commands. Add a readable deployment-config.json defining a
BYO CourseAssistant runtime: CodeZip, PYTHON_3_12, runtime_app.py, HTTP,
PUBLIC networking for OpenAI egress, AWS_IAM authentication, instrumentation
with enableOtel=true, idle timeout 300, and max lifetime 1800 seconds.
Configure agent observability, aws_distro/aws_configurator, HTTP/protobuf OTLP,
trace/log export, Python log instrumentation, EMF metrics, unified trace
destination, disabled automatic openai_agents discovery, and synthetic
content capture. Let the managed runtime supply endpoints/resource identity.
Add prepare_cli.py that validates account/Region/secret ARN, runs agentcore
create --no-agent --skip-install --skip-git into an ignored deployment/Lab12
project, and configures the runtime and aws-targets.json. Copy only agent.py,
runtime_app.py, credentials.py, and telemetry.py to app/CourseAssistant.
Generate its pyproject.toml with every pinned transitive requirements.lock
entry because CodeZip reads that file. Attach additionalPolicies referencing
a scoped secretsmanager:GetSecretValue policy on the provided ARN plus
s3:GetObject for ZIP artifacts in the account/Region default CDK asset bucket.
Use always_on trace sampling for the small lab; document default CDK bootstrap
qualifier and the extra permissions the generated CLI role includes. Never put
the API key in config or package. Validate with agentcore validate. Re-running
preparation must refresh source and preserve CLI deployed state; refuse an
unowned project, changed target, or unexpected source files. Preparation must
not deploy. Keep Agent/Runner visible; this is only deployment preparation.
Add store_secret.py with environment or getpass input, printing only the ARN.
Retain an optional boto3 invoke_runtime.py demonstrating SigV4 invocation,
DEFAULT qualifier, validated session ID, JSON payload, and body closure.
Use agentcore deploy, status, invoke, logs, and traces as the main runbook.
Do not deploy cloud resources while merely creating the lab.
```

## L12-04 — Offline verification

```text
Test actual Agent/RunConfig/tool schema contracts, catalog behavior, key and
secret handling, /ping, invalid JSON and payload rejection, no-key demo, and
AWS invocation arguments/session IDs/body closure. Run the real Runner loop
using a real OpenAIResponsesModel with httpx.MockTransport returning a tool
call and then an assistant message. Verify the function tool executes, its
result feeds the next request, and the real instrumentation library emits
invoke_agent, execute_tool, and chat spans in an in-memory exporter under the
returned trace ID. No offline test may call OpenAI or AWS. Add a separate
subprocess test using the actual ADOT opentelemetry-instrument CLI with
console trace export, disabled logs/metrics/Application Signals, and SDK span
callbacks; verify exported semantic operations. Check deployment configuration,
lockfile, source allowlist, scoped additional IAM policy, and preparation
refresh/target safety. Run the no-key demo. With the pinned real CLI, validate
and package the generated project without AWS deployment; inspect the ZIP
for runtime source, instrumentation, and Linux ARM64 wheels. If possible,
synthesize the generated CDK project locally and check the CodeZip entrypoint,
ADOT startup, environment, and scoped secret policy. Record actual evidence
and unverified live steps in BUILD-LOG.md, organized by prompt ID.
```

## L12-05 — Runbook, exercises, and navigation

```text
Write Markdown lab-brief.md, README.md, exercises.md, and BUILD-LOG.md. Explain
the OpenAI inference/AgentCore hosting boundary, instrumentation vs exporter,
runtime session vs conversation memory, OTEL trace ID vs OpenAI trace ID,
and why tracing_disabled=True would break framework spans. Include isolated
setup, tests, local demo, Node/uv/CLI prerequisites, explicit AWS_PROFILE
selection and aws sso login, successful STS account lookup before preparation,
account/Region selection, safe secret creation, preparation, agentcore deploy
and status, and two CLI invocations sharing one UUID. Explain CLI automatic
Transaction Search setup, permissions warnings, and activation delay. Include
agentcore logs/traces and console inspection, update/redeploy instructions,
evidence checklist, troubleshooting, costs, and cleanup using agentcore remove
all followed by agentcore deploy (both required), dedicated secret deletion,
and retained runtime log cleanup. Preserve shared Transaction Search/CDK
bootstrap resources. Give primary documentation links and date checked.
Distinguish local package/span checks from live CloudWatch ingestion. Update
repository README, prompt index, run-reference guide, test guide, and replay
README. Add a complete matching replay prompt pack at
labs/lab-12-agentcore-runtime/prompt-pack.md.
Do not rename existing labs or change the root environment.
```
