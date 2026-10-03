from pathlib import Path
import sys

import pytest
from agents import Agent, RunConfig
from agents.mcp import MCPServerStdio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mock_data import WEATHER, get_mock_weather, get_public_pool_hours  # noqa: E402
from run_reference import GROUP_ID, build_agent, build_run_config  # noqa: E402


def test_weather_is_mocked_for_exactly_five_cities():
    assert set(WEATHER) == {"Berlin", "London", "New York", "Tokyo", "Sydney"}
    assert get_mock_weather("Berlin") == {
        "source": "mock data", "city": "Berlin", "condition": "light rain", "temperature_c": 14
    }
    with pytest.raises(ValueError, match="Unsupported city"):
        get_mock_weather("Paris")


def test_pool_hours_are_mocked_and_validate_town_and_weekday():
    result = get_public_pool_hours("Riverton", "Saturday")
    assert result["source"] == "mock data"
    assert result["pools"][0] == {
        "pool": "Riverton Central Pool", "opens": "08:00", "closes": "20:00"
    }
    with pytest.raises(ValueError, match="No mock pool schedule"):
        get_public_pool_hours("Cambridge", "Saturday")
    with pytest.raises(ValueError, match="Invalid weekday"):
        get_public_pool_hours("Riverton", "Funday")


def test_sdk_agent_uses_one_local_stdio_mcp_server_with_two_tools():
    params = {"command": sys.executable, "args": [str(ROOT / "mcp_server.py")], "cwd": str(ROOT)}
    server = MCPServerStdio(name="Chapter 10 mock services", params=params)
    agent = build_agent(server)
    assert isinstance(agent, Agent)
    assert agent.mcp_servers == [server]
    assert server.name == "Chapter 10 mock services"


def test_runs_share_trace_group_id_and_metadata():
    config = build_run_config()
    assert isinstance(config, RunConfig)
    assert config.group_id == GROUP_ID == "chapter-10-monitoring-demo"
    assert config.workflow_name == "Chapter 10 mock town services"
    assert config.trace_metadata == {
        "chapter": "10", "lab": "dashboard-monitoring", "data": "mock"
    }


@pytest.mark.asyncio
async def test_stdio_mcp_server_exposes_and_runs_both_local_tools():
    params = {"command": sys.executable, "args": [str(ROOT / "mcp_server.py")], "cwd": str(ROOT)}
    async with MCPServerStdio(name="contract-test", params=params) as server:
        tools = await server.list_tools()
        assert {tool.name for tool in tools} == {"mock_weather", "public_pool_hours"}
        weather = await server.call_tool("mock_weather", {"city": "Tokyo"})
        assert "mock data" in str(weather).lower()
        assert "Tokyo" in str(weather)
