"""Demonstrate SDK-generated memory across two fresh UnixLocal sessions."""

import argparse
import asyncio
import os
import shutil
import tarfile
import uuid
from pathlib import Path

from agents import RunConfig, Runner
from agents.run_config import SandboxRunConfig
from agents.sandbox import LocalSnapshot
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient

from run_sandbox_demo import MODEL_ID, SOLUTION_ROOT, build_agent
from sandbox_manifest import build_manifest

ARTIFACTS_ROOT = SOLUTION_ROOT / "artifacts"
MEMORY_ONLY_INSTRUCTIONS = """
You are conducting a memory-only inspection of the calculator repository
mounted at `repo`; the workspace-root `memories/` directory is managed by the
SDK memory capability. Read files and run tests as requested. Do not edit,
repair, or otherwise change any repository file. Report concrete evidence and
the exact paths/commands you used.
""".strip()

FIRST_PROMPT = """
Read `repo/AGENTS.md` and inspect `repo/calculator.py`. Report one concrete
repository convention and cite its source file and relevant instruction.
Do not run tests or modify files in this run.
""".strip()

SECOND_PROMPT = """
Read the SDK-generated memory in `memories/raw_memories/` and identify the
convention it recorded. Then inspect `repo/AGENTS.md` and
`repo/calculator.py`, and run the repository's prescribed calculator test
command from `repo`. Do not edit or repair anything. Report how the saved
convention applies to the source and what the test results revealed.
""".strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_first_raw_memory(snapshot_path: Path) -> tuple[str, str]:
    """Read the sole generated raw memory directly from the persisted snapshot."""
    with tarfile.open(snapshot_path, "r") as archive:
        members = [
            member
            for member in archive.getmembers()
            if member.isfile()
            and "/memories/raw_memories/" in f"/{member.name.lstrip('./')}"
            and member.name.endswith(".md")
        ]
        require(
            len(members) == 1,
            f"Expected exactly one first-run raw memory in snapshot, found {len(members)}.",
        )
        stream = archive.extractfile(members[0])
        require(stream is not None, f"Could not read snapshot member {members[0].name}.")
        return Path(members[0].name).name, stream.read().decode("utf-8")


async def run_once(agent, client, snapshot, manifest, prompt: str, workflow: str):
    sandbox = await client.create(manifest=manifest, snapshot=snapshot)
    try:
        await sandbox.start()
        return await Runner.run(
            agent,
            prompt,
            run_config=RunConfig(
                workflow_name=workflow,
                group_id=str(uuid.uuid4()),
                sandbox=SandboxRunConfig(session=sandbox),
            ),
            max_turns=20,
        )
    finally:
        # Closing first flushes generated memory and persists the snapshot.
        await sandbox.aclose()
        await client.delete(sandbox)


async def main(model: str) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY to run the API-backed SandboxAgent memory demo.")

    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    snapshot_id = f"memory-demo-{uuid.uuid4()}"
    snapshot = LocalSnapshot(
        id=snapshot_id,
        base_path=ARTIFACTS_ROOT / "memory-snapshots",
    )
    manifest = build_manifest()
    manifest.validated_entries()
    agent = build_agent(model=model, instructions=MEMORY_ONLY_INSTRUCTIONS)
    client = UnixLocalSandboxClient()
    final_export = ARTIFACTS_ROOT / "memory-demo-workspace"

    first_result = await run_once(
        agent, client, snapshot, manifest, FIRST_PROMPT, "lab-03-memory-demo-first"
    )
    require(await snapshot.restorable(), "First sandbox did not persist its LocalSnapshot.")
    snapshot_path = snapshot.base_path / f"{snapshot_id}.tar"
    require(snapshot_path.is_file(), f"Snapshot archive is missing: {snapshot_path}")
    first_raw_name, first_raw_contents = read_first_raw_memory(snapshot_path)
    require(first_raw_contents.strip(), f"First raw memory is empty: {first_raw_name}")

    # Only after validating and retaining the first memory do we create the
    # second session from the same snapshot object.
    second_sandbox = await client.create(manifest=manifest, snapshot=snapshot)
    second_root = Path(second_sandbox.state.manifest.root)
    second_output = None
    try:
        await second_sandbox.start()
        memories_dir = second_root / "memories"
        first_raw_files = sorted((memories_dir / "raw_memories").glob("*.md"))
        require(
            len(first_raw_files) == 1 and first_raw_files[0].name == first_raw_name,
            "First raw memory did not survive snapshot restoration; "
            f"expected {first_raw_name}, found {[path.name for path in first_raw_files]}.",
        )
        require(
            first_raw_files[0].read_text(encoding="utf-8") == first_raw_contents,
            "First raw memory changed during snapshot restoration.",
        )

        # Each Runner.run gets a plain prompt and a distinct group_id; no
        # conversation/session history is shared between the two invocations.
        second_output = await Runner.run(
            agent,
            SECOND_PROMPT,
            run_config=RunConfig(
                workflow_name="lab-03-memory-demo-second",
                group_id=str(uuid.uuid4()),
                sandbox=SandboxRunConfig(session=second_sandbox),
            ),
            max_turns=20,
        )
    finally:
        await second_sandbox.aclose()

    try:
        require(final_export != second_root, "Export path unexpectedly aliases the sandbox.")
        if final_export.exists():
            shutil.rmtree(final_export)
        shutil.copytree(second_root, final_export)
    finally:
        await client.delete(second_sandbox)

    memories_dir = final_export / "memories"
    raw_files = sorted((memories_dir / "raw_memories").glob("*.md"))
    require(
        len(raw_files) == 2,
        f"Expected two distinct SDK raw memories after both runs, found {len(raw_files)}.",
    )
    raw_names = {path.name for path in raw_files}
    require(len(raw_names) == 2, "SDK generated duplicate raw-memory filenames.")
    retained_first = memories_dir / "raw_memories" / first_raw_name
    require(retained_first.is_file(), f"First raw memory did not survive: {retained_first}")
    require(
        retained_first.read_text(encoding="utf-8") == first_raw_contents,
        f"First raw memory changed during the second run: {retained_first}",
    )

    summary_files = sorted((memories_dir / "rollout_summaries").glob("*.md"))
    summary_ids = {path.name.split("_", 1)[0] for path in summary_files}
    raw_ids = {path.stem for path in raw_files}
    require(
        len(summary_files) == 2 and summary_ids == raw_ids,
        "Expected one matching rollout_summaries/*.md file for each raw memory; "
        f"raw IDs={sorted(raw_ids)}, summary IDs={sorted(summary_ids)}.",
    )

    print("Verified SDK-generated memory across two SandboxAgent runs.")
    print(f"Snapshot: {snapshot.base_path / (snapshot_id + '.tar')}")
    print(f"Exported workspace: {final_export}")
    print("Raw memories:")
    for path in raw_files:
        print(f"  {path}")
    print("Rollout summaries:")
    for path in summary_files:
        print(f"  {path}")
    print(f"\nFirst run final output:\n{first_result.final_output}")
    print(f"\nSecond run final output:\n{second_output.final_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=os.environ.get("OPENAI_SANDBOX_MODEL", MODEL_ID))
    asyncio.run(main(parser.parse_args().model))
