import io
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import httpx
from agents import Agent, RunConfig
from agents.models.openai_responses import OpenAIResponsesModel
from openai import AsyncOpenAI
from opentelemetry import baggage
from pydantic import ValidationError
import pytest
from starlette.testclient import TestClient

from agent import build_agent, build_run_config, course_info
import credentials
from invoke_runtime import invoke_remote
import runtime_app

ROOT = Path(__file__).resolve().parents[1]
SESSION = "lab12-offline-session-0000000000000001"


def test_sdk_objects_and_tool_schema():
    agent = build_agent()
    config = build_run_config(SESSION)
    assert isinstance(agent, Agent)
    assert isinstance(config, RunConfig)
    assert agent.model == os.getenv("OPENAI_MODEL", "gpt-6-luna")
    assert config.group_id == SESSION and config.tracing_disabled is False
    assert config.trace_metadata["data"] == "synthetic"
    assert agent.tools[0].name == "get_course_info"
    schema = agent.tools[0].params_json_schema
    assert schema["required"] == ["topic"] and schema["additionalProperties"] is False
    assert course_info(" Observability ").startswith("Synthetic course data.")
    assert "Unknown topic" in course_info("unknown")


@pytest.mark.parametrize("payload", [{}, {"prompt": " "}, {"prompt": 3}, {"prompt": "a" * 2001}, {"prompt": "ok", "key": "secret"}, []])
def test_bad_payload_never_reaches_runner(monkeypatch, payload):
    runner = Mock(side_effect=AssertionError("Runner must not execute"))
    monkeypatch.setattr(runtime_app.Runner, "run", runner)
    with TestClient(runtime_app.app) as client:
        response = client.post("/invocations", json=payload)
    assert response.status_code == 400
    assert "secret" not in response.text
    runner.assert_not_called()


def test_ping_and_invalid_json():
    with TestClient(runtime_app.app) as client:
        assert client.get("/ping").json()["status"] == "Healthy"
        assert client.post("/invocations", content="not json").status_code == 400


def test_secret_lookup_is_scoped_and_not_put_in_environment(monkeypatch):
    secrets = Mock()
    secrets.get_secret_value.return_value = {"SecretString": '{"OPENAI_API_KEY": "test-only-key"}'}
    monkeypatch.setenv("OPENAI_API_KEY_SECRET_ARN", "arn:aws:secretsmanager:us-east-1:123456789012:secret:lab12-key")
    factory = Mock(return_value=secrets)
    monkeypatch.setattr(credentials.boto3, "client", factory)
    assert credentials.load_api_key() == "test-only-key"
    factory.assert_called_once_with("secretsmanager")
    secrets.get_secret_value.assert_called_once_with(SecretId=os.environ["OPENAI_API_KEY_SECRET_ARN"])
    assert "OPENAI_API_KEY" not in os.environ
    secrets.get_secret_value.return_value = {"SecretString": '{"OPENAI_API_KEY": 123}'}
    with pytest.raises(RuntimeError, match="nonempty"):
        credentials.load_api_key()


def test_local_key_and_missing_credentials(monkeypatch):
    with pytest.raises(RuntimeError, match="Set OPENAI_API_KEY"):
        credentials.load_api_key()
    monkeypatch.setenv("OPENAI_API_KEY", " test-only-local ")
    monkeypatch.setattr(credentials.boto3, "client", Mock(side_effect=AssertionError("No AWS lookup")))
    assert credentials.load_api_key() == "test-only-local"
    set_key = Mock()
    monkeypatch.setattr(credentials, "set_default_openai_key", set_key)
    credentials.configure_openai()
    set_key.assert_called_once_with("test-only-local", use_for_tracing=False)


def test_remote_invocation_closes_body_and_forwards_session():
    body = io.BytesIO(b'{"final_output": "Synthetic data", "otel_trace_id": "123"}')
    client = Mock()
    client.invoke_agent_runtime.return_value = {"response": body}
    result = invoke_remote(client, "arn:runtime", "Course?", SESSION)
    assert result["final_output"] == "Synthetic data" and body.closed
    args = client.invoke_agent_runtime.call_args.kwargs
    assert args["runtimeSessionId"] == SESSION and args["qualifier"] == "DEFAULT"
    assert json.loads(args["payload"]) == {"prompt": "Course?"}
    with pytest.raises(ValueError, match="33"):
        invoke_remote(client, "arn:runtime", "Course?", "too-short")
    with pytest.raises(ValidationError):
        invoke_remote(client, "arn:runtime", " ", SESSION)
    assert client.invoke_agent_runtime.call_count == 1


def test_demo_skips_without_credentials():
    process = subprocess.run([sys.executable, "run_reference.py"], cwd=ROOT, env=os.environ.copy(),
                             capture_output=True, text=True, timeout=10)
    assert process.returncode == 0 and "SKIP" in process.stdout


async def test_real_sdk_loop_and_instrumentation_without_network(monkeypatch, span_exporter):
    calls = []

    def respond(request):
        calls.append(json.loads(request.content))
        if len(calls) == 1:
            output = [{"type": "function_call", "id": "fc_1", "call_id": "call_1",
                       "name": "get_course_info", "arguments": '{"topic":"observability"}', "status": "completed"}]
        else:
            assert any(item.get("type") == "function_call_output" and "Synthetic course data" in item["output"]
                       for item in calls[-1]["input"])
            output = [{"type": "message", "id": "msg_1", "role": "assistant", "status": "completed",
                       "content": [{"type": "output_text", "text": "Synthetic course: ADOT exports SDK spans to CloudWatch.", "annotations": []}]}]
        return httpx.Response(200, json={
            "id": f"resp_{len(calls)}", "object": "response", "created_at": 0,
            "model": "gpt-6-luna", "status": "completed", "output": output,
            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15,
                      "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}},
        })

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        openai = AsyncOpenAI(api_key="test-only-never-sent-to-network", http_client=transport)
        agent = build_agent()
        agent.model = OpenAIResponsesModel(model="gpt-6-luna", openai_client=openai)
        monkeypatch.setattr(runtime_app, "build_agent", lambda: agent)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=runtime_app.app), base_url="http://lab") as client:
            response = await client.post("/invocations", json={"prompt": "Observability course?"},
                                         headers={"X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": SESSION})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["last_agent"] == "course_assistant" and result["runtime_session_id"] == SESSION
    assert len(calls) == 2 and len(result["tool_outputs"]) == 1
    assert result["usage"] == {"input_tokens": 20, "output_tokens": 10}
    spans = span_exporter.get_finished_spans()
    operations = {span.attributes.get("gen_ai.operation.name") for span in spans}
    assert {"invoke_agent", "execute_tool", "chat"} <= operations
    assert all(format(span.context.trace_id, "032x") == result["otel_trace_id"] for span in spans)
    root = next(span for span in spans if span.name == "lab12.invocation")
    assert root.attributes["session.id"] == SESSION
    assert baggage.get_baggage("session.id") is None

