"""AgentCore HTTP contract: /ping and /invocations on port 8080."""

import uuid

from agents import Runner, ToolCallOutputItem
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.runtime.context import RequestContext
from opentelemetry import baggage, context as otel_context, trace
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from starlette.exceptions import HTTPException

from agent import build_agent, build_run_config

app = BedrockAgentCoreApp()


class InvocationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    prompt: str = Field(min_length=1, max_length=2000)

    @field_validator("prompt")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt must not be blank")
        return value.strip()


@app.entrypoint
async def invoke(payload: dict, context: RequestContext) -> dict:
    try:
        request = InvocationRequest.model_validate(payload)
    except ValidationError:
        # Avoid echoing invalid input (or arbitrary fields) into runtime logs.
        raise HTTPException(400, "Provide only a nonblank string prompt, at most 2000 characters.")

    session_id = context.session_id or str(uuid.uuid4())
    token = otel_context.attach(baggage.set_baggage("session.id", session_id))
    try:
        # SDK workflow spans inherit this span's OTEL trace, which is returned
        # for CloudWatch lookup. The OpenAI SDK trace ID is a different ID.
        with trace.get_tracer("lab12.runtime").start_as_current_span(
            "lab12.invocation", attributes={"session.id": session_id, "lab.id": "12"}
        ) as span:
            result = await Runner.run(
                build_agent(), request.prompt,
                run_config=build_run_config(session_id), max_turns=4,
            )
            usage = result.context_wrapper.usage
            return {
                "final_output": str(result.final_output),
                "last_agent": result.last_agent.name,
                "tool_outputs": [
                    str(item.output) for item in result.new_items
                    if isinstance(item, ToolCallOutputItem)
                ],
                "runtime_session_id": session_id,
                "otel_trace_id": format(span.get_span_context().trace_id, "032x"),
                "usage": {"input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens},
            }
    finally:
        otel_context.detach(token)


if __name__ == "__main__":
    from credentials import configure_openai
    from telemetry import instrument_agents

    instrument_agents()
    configure_openai()
    app.run(host="0.0.0.0", port=8080)
