"""Synthetic SDK manifest for the tiny calculator workspace."""

from pathlib import Path

from agents.sandbox import Manifest
from agents.sandbox.entries import Dir, File
from agents.run_config import SandboxRunConfig
from agents import RunConfig
from agents.sandbox.sandboxes.unix_local import (
    UnixLocalSandboxClient,
    UnixLocalSandboxClientOptions,
)

CALCULATOR_ROOT = Path(__file__).parent / "calculator"
SKILL_ROOT = Path(__file__).parent / "skills" / "debug-failing-tests"
MEMORY_ROOT = Path(__file__).parent / "memories"


def build_manifest() -> Manifest:
    """Mount calculator files at the relative workspace path ``repo``."""
    files = {
        "AGENTS.md": File(content=(CALCULATOR_ROOT / "AGENTS.md").read_bytes()),
        "calculator.py": File(content=(CALCULATOR_ROOT / "calculator.py").read_bytes()),
        "tests": Dir(
            children={
                "test_calculator.py": File(
                    content=(CALCULATOR_ROOT / "tests" / "test_calculator.py").read_bytes()
                )
            }
        ),
    }
    skill = Dir(
        children={
            "SKILL.md": File(content=(SKILL_ROOT / "SKILL.md").read_bytes()),
        }
    )
    memories = Dir(
        children={
            "MEMORY.md": File(content=(MEMORY_ROOT / "MEMORY.md").read_bytes()),
            "memory_summary.md": File(
                content=(MEMORY_ROOT / "memory_summary.md").read_bytes()
            ),
        }
    )
    return Manifest(
        entries={
            "repo": Dir(children=files),
            "skills/debug-failing-tests": skill,
            "memories": memories,
        }
    )


def build_unix_local_run_config() -> RunConfig:
    """Return a RunConfig that materializes this lab manifest with UnixLocal."""
    manifest = build_manifest()
    return RunConfig(
        workflow_name="lab-03-sandboxagent-unix-local",
        sandbox=SandboxRunConfig(
            client=UnixLocalSandboxClient(),
            options=UnixLocalSandboxClientOptions(),
            manifest=manifest,
        ),
    )
