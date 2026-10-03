"""Run the calculator debugging exercise in a UnixLocal SandboxAgent."""

import asyncio
import argparse
import json
import os
import shutil
from pathlib import Path

from agents import Runner, RunConfig
from agents.items import ToolCallItem, ToolCallOutputItem
from agents.sandbox import SandboxAgent
from agents.sandbox import MemoryGenerateConfig, MemoryLayoutConfig, MemoryReadConfig
from agents.sandbox.capabilities import Filesystem, Memory, Shell, Skills
from agents.sandbox.entries import Dir
from agents.run_config import SandboxRunConfig
from agents.sandbox import LocalSnapshotSpec
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient

from sandbox_instructions import SANDBOX_AGENT_INSTRUCTIONS
from sandbox_manifest import build_manifest, build_unix_local_run_config

MODEL_ID = "gpt-6-luna"
SOLUTION_ROOT = Path(__file__).parent
ARTIFACTS_ROOT = SOLUTION_ROOT / "artifacts"


def build_agent(
    model: str = MODEL_ID, instructions: str = SANDBOX_AGENT_INSTRUCTIONS
) -> SandboxAgent:
    skill_file = (
        build_manifest()
        .validated_entries()["skills/debug-failing-tests"]
        .children["SKILL.md"]
    )
    return SandboxAgent(
        name="calculator_debugger",
        instructions=instructions,
        model=model,
        default_manifest=build_manifest(),
        capabilities=[
            Filesystem(),
            Shell(),
            Skills(from_=Dir(children={"debug-failing-tests": Dir(children={"SKILL.md": skill_file})})),
            Memory(
                layout=MemoryLayoutConfig(memories_dir="memories", sessions_dir="sessions"),
                read=MemoryReadConfig(live_update=True),
                generate=MemoryGenerateConfig(
                    phase_one_model=model,
                    phase_two_model=model,
                    extra_prompt=(
                        "Preserve repository conventions, prefer the smallest fixes, "
                        "and record verification commands that worked."
                    ),
                ),
            ),
        ],
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Debug the calculator in a UnixLocal sandbox.")
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Use Runner.run instead of streaming progress with Runner.run_streamed.",
    )
    parser.add_argument("--model", default=os.environ.get("OPENAI_SANDBOX_MODEL", MODEL_ID))
    args = parser.parse_args()
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY to run the API-backed SandboxAgent demo.")

    agent = build_agent(args.model)
    base_config = build_unix_local_run_config()
    manifest = base_config.sandbox.manifest
    entries = manifest.validated_entries()
    print("Sandbox startup: runtime=UnixLocal")
    print(f"Workspace entries: {', '.join(str(path) for path in entries)}")

    prompt = (
        "Debug the failing calculator test in repo. Follow the repository "
        "instructions, including writing and verifying the durable repo "
        "convention note in the sandbox-root memories directory."
    )
    client = UnixLocalSandboxClient()
    sandbox = await client.create(
        manifest=manifest,
        snapshot=LocalSnapshotSpec(base_path=ARTIFACTS_ROOT / "snapshots"),
    )
    workspace_root = Path(sandbox.state.manifest.root)
    run_config = RunConfig(
        workflow_name="lab-03-sandboxagent-unix-local",
        sandbox=SandboxRunConfig(session=sandbox),
    )
    try:
        async with sandbox:
            if args.no_stream:
                result = await Runner.run(agent, prompt, run_config=run_config, max_turns=20)
                print(f"Final output:\n{result.final_output}")
            else:
                streamed = Runner.run_streamed(agent, prompt, run_config=run_config, max_turns=20)
                model_text_started = False
                async for event in streamed.stream_events():
                    if event.type == "raw_response_event" and event.data.type == "response.output_text.delta":
                        if not model_text_started:
                            print("\n[model] ", end="", flush=True)
                            model_text_started = True
                        print(event.data.delta, end="", flush=True)
                    elif event.type == "run_item_stream_event":
                        item = event.item
                        if event.name == "tool_called" and isinstance(item, ToolCallItem):
                            model_text_started = False
                            raw_item = item.raw_item
                            arguments = raw_item.get("arguments") if isinstance(raw_item, dict) else getattr(raw_item, "arguments", None)
                            try:
                                arguments = json.dumps(json.loads(arguments), indent=2) if arguments else "{}"
                            except (json.JSONDecodeError, TypeError):
                                arguments = str(arguments)
                            print(f"\n[tool call] {item.tool_name or 'unknown'}\n{arguments}")
                        elif event.name == "tool_output" and isinstance(item, ToolCallOutputItem):
                            print(f"\n[tool output] {item.output}")
                print(f"\nFinal output:\n{streamed.final_output}")
    finally:
        # Session shutdown flushes SDK-generated memory before the temporary workspace is copied.
        ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
        exported = ARTIFACTS_ROOT / "latest-workspace"
        if exported.exists():
            shutil.rmtree(exported)
        if workspace_root.exists():
            shutil.copytree(workspace_root, exported)
            print(f"Exported sandbox workspace: {exported}")
        await client.delete(sandbox)


if __name__ == "__main__":
    asyncio.run(main())
