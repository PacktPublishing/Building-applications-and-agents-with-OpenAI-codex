import json
import os
from pathlib import Path
import subprocess
import sys


def test_adot_cli_bootstrap_exports_sdk_spans_to_console():
    root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": str(root),
        "OTEL_PYTHON_DISTRO": "aws_distro",
        "OTEL_PYTHON_CONFIGURATOR": "aws_configurator",
        "OTEL_PYTHON_DISABLED_INSTRUMENTATIONS": "openai_agents",
        "OTEL_TRACES_EXPORTER": "console",
        "OTEL_METRICS_EXPORTER": "none",
        "OTEL_LOGS_EXPORTER": "none",
        "OTEL_AWS_APPLICATION_SIGNALS_ENABLED": "false",
        # Agent mode skips AWS infrastructure metadata discovery. All spans
        # are sampled and go only to console; the unsampled export path stays
        # empty. A local unused endpoint prevents deriving AWS export endpoints.
        "AGENT_OBSERVABILITY_ENABLED": "true",
        "OTEL_TRACES_SAMPLER": "always_on",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:1",
        "AWS_EC2_METADATA_DISABLED": "true",
        "AWS_REGION": "us-east-1",
        "OTEL_SERVICE_NAME": "lab12_offline_probe",
    })
    command = [str(Path(sys.executable).parent / "opentelemetry-instrument"), sys.executable, "tests/adot_probe.py"]
    process = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, timeout=30)
    assert process.returncode == 0, process.stderr
    assert "offline probe blocked network" not in process.stderr
    decoder = json.JSONDecoder()
    spans = []
    text = process.stdout.strip()
    while text:
        value, end = decoder.raw_decode(text)
        spans.append(value)
        text = text[end:].lstrip()
    assert {"invoke_agent", "execute_tool", "chat"} <= {s["attributes"].get("gen_ai.operation.name") for s in spans}
    assert all(s["resource"]["attributes"]["service.name"] == "lab12_offline_probe" for s in spans)
