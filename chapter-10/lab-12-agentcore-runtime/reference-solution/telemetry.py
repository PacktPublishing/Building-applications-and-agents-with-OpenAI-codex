"""Bridge SDK tracing to the tracer provider installed by ADOT at startup."""

from opentelemetry.instrumentation.openai_agents import OpenAIAgentsInstrumentor


def instrument_agents(*, tracer_provider=None) -> None:
    # Docker disables auto-discovery for openai_agents only, so this explicit
    # registration occurs once. ADOT still configures the OTLP exporters and
    # instruments HTTP, ASGI, boto3, etc. Do not replace ADOT's global provider.
    # Replacing SDK processors routes SDK traces solely through OpenTelemetry.
    OpenAIAgentsInstrumentor(replace_existing_processors=True).instrument(
        tracer_provider=tracer_provider
    )
