"""Run two mock-service requests and group their traces for dashboard review."""

import asyncio
import os
import sys
from pathlib import Path

from agents import Agent, RunConfig, Runner
from agents.mcp import MCPServerStdio

ROOT = Path(__file__).resolve().parent
GROUP_ID = "chapter-10-monitoring-demo"


def build_agent(server: MCPServerStdio) -> Agent:
    return Agent(
        name="Town Services Assistant",
        model="gpt-6-luna",
        instructions=(
            "Answer using the local mock MCP tools. Always identify results as mock data. "
            "Use mock_weather for weather and public_pool_hours for swimming pool hours. "
            "The only supported town is the fictional town Riverton."
        ),
        mcp_servers=[server],
    )


def build_run_config() -> RunConfig:
    return RunConfig(
        workflow_name="Chapter 10 mock town services",
        group_id=GROUP_ID,
        trace_metadata={"chapter": "10", "lab": "dashboard-monitoring", "data": "mock"},
    )


async def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: set OPENAI_API_KEY to run the model-backed demo.")
        return 0

    params = {"command": sys.executable, "args": [str(ROOT / "mcp_server.py")], "cwd": str(ROOT)}
    async with MCPServerStdio(name="Chapter 10 mock services", params=params) as server:
        agent = build_agent(server)
        config = build_run_config()
        for label, prompt in (
            ("Weather", "What is the mock weather in Berlin?"),
            ("Pool hours", "What are the public pool opening hours in Riverton on Saturday?"),
        ):
            result = await Runner.run(agent, prompt, run_config=config)
            print(f"{label}: {result.final_output}\n")
    print(f"Find both traces using group ID: {GROUP_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
