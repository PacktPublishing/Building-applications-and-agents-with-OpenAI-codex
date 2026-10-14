# Chapter 10 Lab 12 build log

Built on 6 October 2026 from the lab-level prompt pack in order.

## L12-01 — SDK agent and tool

- Read the repo-local `openai-agents-sdk` Skill, core and testing references,
  and official SDK `examples/basic/tools.py` and `tests/fake_model.py` patterns.
- Consulted the OpenAI Docs MCP quickstart for current Agent/Runner guidance.
- Built a real `Agent` with one deterministic synthetic function tool and
  `RunConfig` workflow/group metadata. Default model: `gpt-6-luna`.
- Installed an isolated Python 3.12 environment; pinned OpenAI Agents 0.23.1,
  AgentCore SDK 1.24.0, ADOT 0.21.0, OpenAI Agents OTel instrumentation 0.62.4.
  Compiled universal transitive `requirements.lock` for Python 3.12.
- Kept the root course environment and SDK submodule pin unchanged.

## L12-02 — Runtime and telemetry

- Added `BedrockAgentCoreApp`, strict input validation, direct `Runner.run`,
  session baggage, and a parent invocation span. Response includes actual
  tool outputs, token usage, runtime session ID, and OTEL trace ID.
- Added startup-only secret loading and local key support with no import-time
  AWS lookup. Key never appears in image, template, request, or response.
- Added explicit `OpenAIAgentsInstrumentor` registration that replaces the
  OpenAI export processor while retaining SDK tracing callbacks. ADOT owns
  provider/export configuration. Disabled only duplicate auto-discovery.
- Actual library tests confirm `invoke_agent`, `chat`, and `execute_tool`
  spans, including the real Responses model path through mock HTTP.

## L12-03 — AgentCore CLI deployment

- Revised deployment at the user's request to use the current Node CLI
  `@aws/agentcore@0.31.1`. Consulted official CLI configuration, commands,
  permissions, and Transaction Search docs and the AWS Python CodeZip guide.
- Replaced hand-written Docker/ECR/CloudFormation artifacts with CodeZip
  configuration, local `prepare_cli.py`, and CLI-managed CDK infrastructure.
- Preparation uses the real CLI's `create --no-agent` and `validate`, writes
  the selected target, copies only runtime sources, and generates a Python
  project containing all transitive dependency pins from `requirements.lock`.
- Enabled CLI-managed ADOT launch, explicit instrumentation, public egress,
  inbound IAM authentication, synthetic content capture, and always-on lab
  sampling. Preserved scoped Secrets Manager access, safe secret helper,
  optional low-level SigV4 client, and session limits.
- Local synthesis exposed missing S3 code-asset read access in the generated
  role. Added it through the CLI-supported `additionalPolicies` document,
  scoped to ZIP artifacts in the selected account/Region's default CDK bucket.
  Documented the default qualifier and the generated role's unused Bedrock
  and configuration-bundle permissions.
- No AWS resources were deployed or changed while creating or revising this lab.

## L12-04 — Verification

Commands run from this reference directory unless noted:

```bash
.venv/bin/python -m pytest -q
env -u OPENAI_API_KEY -u OPENAI_API_KEY_SECRET_ARN .venv/bin/python run_reference.py
.venv/bin/python -m compileall -q agent.py credentials.py telemetry.py runtime_app.py run_reference.py invoke_runtime.py store_secret.py prepare_cli.py
# Preparation used an illustrative account/secret ARN and a temporary CLI install.
# Inside the generated deployment/Lab12 project:
agentcore validate
agentcore package --runtime CourseAssistant
# Inside its agentcore/cdk directory, after installing generated dependencies:
npm run cdk -- synth --quiet --no-lookups
```

- Offline suite: **17 passed, 1 skipped**. The skipped test is the explicit
  opt-in live OpenAI smoke test. No model or AWS calls occurred in offline tests.
- Real SDK loop: two mock Responses requests, actual function execution,
  tool result in the second request, expected usage aggregation, and
  `invoke_agent`, `chat`, and `execute_tool` spans under one returned OTEL ID.
- Actual ADOT CLI bootstrap: passed in a subprocess with console export and
  cloud logs/metrics disabled. SDK callbacks produced semantic framework spans.
- Preparation contracts: valid CodeZip/ADOT settings, pinned dependencies,
  scoped secret/S3 policy, allowed source set, state-preserving refresh,
  unowned-project rejection, and account/Region validation.
- Real AgentCore CLI: version 0.31.1, fresh creation, repeated preparation,
  schema validation, and successful CodeZip packaging (CLI reports 39.97 MB).
  ZIP contains four runtime sources, ADOT and Agents instrumentation packages,
  and 13 Linux ELF shared libraries, all ARM64. No tests/local environment or
  credentials were included. Sources and dependencies were packaged locally.
- Generated CDK TypeScript compilation and synthesis: passed with AWS lookups
  disabled and dependency downloads disabled during synthesis. Verified
  Python 3.12 CodeZip, `['opentelemetry-instrument', 'runtime_app.py']`
  entrypoint, ADOT environment, lifetimes, and scoped secret/S3 permissions.
- CLI and CDK public dependencies were installed in temporary/generated
  directories; the root course environment was left unchanged. Generated CDK
  npm installation reported upstream dependency audit findings; dependencies
  were retained as generated rather than applying breaking upgrades.
- No-key demo exits successfully with `SKIP`; Python compilation passes.
- AgentCore SDK emits upstream Pydantic and `datetime.utcnow()` deprecation
  warnings; these do not fail the suite.
- AWS deployment, managed telemetry export, Transaction Search
  activation, CLI live invocation/traces/teardown, and CloudWatch ingestion
  remain unverified. Complete the runbook's live evidence checklist.

## L12-05 — Teaching materials and replay

- Added lab brief, architecture, CLI deployment runbook, exercises, primary
  documentation links, credential instructions, observability troubleshooting,
  live evidence criteria, and resource cleanup.
- Updated repository README, prompt index, run-reference guide, test guide,
  and replay README. Added the full replay prompt pack under
  `replay-environment/labs/lab-12-agentcore-runtime/`.
- Confirmed replay prompt pack matches the lab-level pack. Existing lab folders
  were not renamed. Existing untracked `improvement.md` was left untouched.

- Updated the complete replay prompt pack and course navigation for the CLI
  workflow, including updates and `remove all` followed by `deploy` teardown.

## Credential setup repair

- The user reported the opt-in live OpenAI smoke test passed: 1 passed, with
  one upstream AgentCore/Pydantic deprecation warning, in 5.90 seconds.
- Their AWS setup then failed because the selected login credential provider
  needed botocore CRT support and STS failed with an OAuth token error. The
  failed STS lookup left LAB12_ACCOUNT_ID empty, causing preparation validation.
- Added pinned botocore[crt] 1.43.108 to requirements and regenerated the lock;
  awscrt 0.36.0 is now included. Installed it into the isolated lab environment.
- Confirmed pumpingcode is an SSO-configured profile without reading or logging
  credential values. No SSO login, secret creation, or deployment was performed.
- Updated the runbook to select AWS_PROFILE explicitly, refresh SSO login,
  and confirm STS success before continuing. Updated replay instructions.
- Repair verification: 17 passed, 1 skipped; botocore HAS_CRT enabled,
  awscrt imports successfully, and its Python 3.12 Linux ARM64 wheel was
  downloaded and verified as ELF/AArch64. No live AWS calls were made.
