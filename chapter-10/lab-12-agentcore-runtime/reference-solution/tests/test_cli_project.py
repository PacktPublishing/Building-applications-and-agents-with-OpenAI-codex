import json
from pathlib import Path
import tomllib
from unittest.mock import Mock

import pytest

import prepare_cli

ACCOUNT = "123456789012"
REGION = "us-east-1"
SECRET = f"arn:aws:secretsmanager:{REGION}:{ACCOUNT}:secret:lab12-test-AbCdEf"


def skeleton(tmp_path):
    project = tmp_path / "Lab12"
    (project / "agentcore/.cli").mkdir(parents=True)
    (project / "agentcore/agentcore.json").write_text(json.dumps({"name": "Lab12", "version": 1}))
    (project / prepare_cli.MARKER).touch()
    (project / "agentcore/aws-targets.json").write_text(json.dumps([
        {"name": "default", "account": ACCOUNT, "region": REGION}]))
    return project


def test_codezip_contract_and_scoped_secret(tmp_path):
    project = skeleton(tmp_path)
    prepare_cli.write_project(project, ACCOUNT, REGION, SECRET, "gpt-6-luna")
    config = json.loads((project / "agentcore/agentcore.json").read_text())
    runtime = config["runtimes"][0]
    assert runtime["build"] == "CodeZip" and runtime["runtimeVersion"] == "PYTHON_3_12"
    assert runtime["protocol"] == "HTTP" and runtime["networkMode"] == "PUBLIC"
    assert runtime["authorizerType"] == "AWS_IAM"
    assert runtime["instrumentation"] == {"enableOtel": True}
    assert runtime["lifecycleConfiguration"] == {"idleRuntimeSessionTimeout": 300, "maxLifetime": 1800}
    env = {entry["name"]: entry["value"] for entry in runtime["envVars"]}
    assert "OPENAI_API_KEY" not in env and env["OPENAI_API_KEY_SECRET_ARN"] == SECRET
    assert env["AGENT_OBSERVABILITY_ENABLED"] == "true" and env["OTEL_METRICS_EXPORTER"] == "awsemf"
    assert env["OTEL_PYTHON_DISABLED_INSTRUMENTATIONS"] == "openai_agents"
    app = project / runtime["codeLocation"]
    policy = json.loads((app / runtime["additionalPolicies"][0]).read_text())
    assert policy["Statement"][0] == {"Sid": "ReadOpenAIKey", "Effect": "Allow",
                                      "Action": ["secretsmanager:GetSecretValue"], "Resource": SECRET}
    assert policy["Statement"][1] == {"Sid": "ReadCodeZip", "Effect": "Allow", "Action": ["s3:GetObject"],
                                      "Resource": f"arn:aws:s3:::cdk-hnb659fds-assets-{ACCOUNT}-{REGION}/*.zip"}
    pyproject = tomllib.loads((app / "pyproject.toml").read_text())
    deps = pyproject["project"]["dependencies"]
    assert "aws-opentelemetry-distro==0.21.0" in deps
    assert "opentelemetry-instrumentation-openai-agents==0.62.4" in deps
    assert all("==" in dep for dep in deps)
    assert {p.relative_to(app).as_posix() for p in app.rglob("*") if p.is_file()} == {
        *prepare_cli.RUNTIME_FILES, "pyproject.toml", "policies/openai-secret.json"}


def test_refresh_preserves_deployed_state_and_never_deploys(tmp_path, monkeypatch):
    project = skeleton(tmp_path)
    state = project / "agentcore/.cli/deployed-state.json"
    state.write_text('{"runtime": "existing"}')
    run = Mock(return_value=Mock(stdout=prepare_cli.CLI_VERSION))
    monkeypatch.setattr(prepare_cli.subprocess, "run", run)
    prepare_cli.prepare(project, ACCOUNT, REGION, SECRET, "another-model", "agentcore")
    assert state.read_text() == '{"runtime": "existing"}'
    assert [call.args[0] for call in run.call_args_list] == [["agentcore", "--version"], ["agentcore", "validate"]]
    prepare_cli.write_project(project, ACCOUNT, REGION, SECRET, "gpt-6-luna")
    app = project / "app/CourseAssistant"
    (app / ".env").write_text("DO_NOT_PACKAGE=anything")
    with pytest.raises(ValueError, match="unexpected"):
        prepare_cli.write_project(project, ACCOUNT, REGION, SECRET, "gpt-6-luna")


def test_refuse_unowned_project_and_cross_account_target(tmp_path, monkeypatch):
    run = Mock(return_value=Mock(stdout=prepare_cli.CLI_VERSION))
    monkeypatch.setattr(prepare_cli.subprocess, "run", run)
    project = skeleton(tmp_path)
    (project / prepare_cli.MARKER).unlink()
    with pytest.raises(ValueError, match="overwrite"):
        prepare_cli.prepare(project, ACCOUNT, REGION, SECRET, "gpt-6-luna", "agentcore")
    (project / prepare_cli.MARKER).touch()
    with pytest.raises(ValueError, match="different AWS account"):
        prepare_cli.prepare(project, "111111111111", REGION, SECRET.replace(ACCOUNT, "111111111111"),
                            "gpt-6-luna", "agentcore")
    with pytest.raises(ValueError, match="selected account"):
        prepare_cli.validate_target(ACCOUNT, "us-west-2", SECRET)
