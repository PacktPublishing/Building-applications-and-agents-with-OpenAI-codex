"""Explicit opt-in live model check; never creates AWS resources."""

import os
import uuid

from bedrock_agentcore.runtime.context import RequestContext
import pytest

import credentials
from runtime_app import invoke

LIVE_KEY = os.getenv("OPENAI_API_KEY", "")
LIVE_ENABLED = os.getenv("RUN_AGENTCORE_OPENAI_SMOKE") == "1"


@pytest.mark.skipif(not LIVE_ENABLED or not LIVE_KEY, reason="Set RUN_AGENTCORE_OPENAI_SMOKE=1 and OPENAI_API_KEY for a live model call.")
async def test_openai_demo(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", LIVE_KEY)
    credentials.configure_openai()
    result = await invoke(
        {"prompt": "Use get_course_info to tell me what the observability course covers."},
        RequestContext(session_id=str(uuid.uuid4())),
    )
    assert result["final_output"] and result["last_agent"] == "course_assistant"
    assert result["tool_outputs"] and "Synthetic course data." in result["tool_outputs"][0]
    assert result["usage"]["input_tokens"] > 0
