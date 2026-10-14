import pytest
from agents import set_trace_processors
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from telemetry import instrument_agents


@pytest.fixture(scope="session")
def span_exporter():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    instrument_agents(tracer_provider=provider)
    yield exporter
    set_trace_processors([])
    provider.shutdown()


@pytest.fixture(autouse=True)
def offline_environment(monkeypatch, span_exporter):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY_SECRET_ARN", raising=False)
    monkeypatch.delenv("OPENAI_AGENTS_DISABLE_TRACING", raising=False)
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    span_exporter.clear()
