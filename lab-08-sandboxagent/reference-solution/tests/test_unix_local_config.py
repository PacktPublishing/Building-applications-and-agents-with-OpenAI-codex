import sys
from pathlib import Path

SOLUTION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOLUTION_ROOT))

from agents import RunConfig
from agents.run_config import SandboxRunConfig
from agents.sandbox.entries import Dir
from agents.sandbox import MemoryGenerateConfig, MemoryLayoutConfig, MemoryReadConfig
from agents.sandbox.capabilities import Filesystem, Memory, Shell, Skills
from agents.sandbox.sandboxes.unix_local import (
    UnixLocalSandboxClient,
    UnixLocalSandboxClientOptions,
)

from sandbox_manifest import build_manifest, build_unix_local_run_config
from run_sandbox_demo import MODEL_ID, build_agent


def test_manifest_uses_relative_repo_and_validates():
    manifest = build_manifest()
    entries = manifest.validated_entries()

    assert "repo" in entries
    assert all(not str(path).startswith("/") for path in entries)
    assert isinstance(entries["repo"], Dir)
    assert "memories" in entries
    memory_files = entries["memories"].children
    assert set(memory_files) == {"MEMORY.md", "memory_summary.md"}
    assert memory_files["MEMORY.md"].content
    assert memory_files["memory_summary.md"].content


def test_unix_local_run_config_is_constructible():
    config = build_unix_local_run_config()

    assert isinstance(config, RunConfig)
    assert isinstance(config.sandbox, SandboxRunConfig)
    assert isinstance(config.sandbox.client, UnixLocalSandboxClient)
    assert isinstance(config.sandbox.options, UnixLocalSandboxClientOptions)
    assert config.sandbox.manifest.validated_entries()


def test_demo_uses_requested_model():
    assert MODEL_ID == "gpt-6-luna"
    assert build_agent().model == "gpt-6-luna"


def test_agent_has_explicit_memory_and_required_capabilities():
    agent = build_agent()
    by_type = {capability.type: capability for capability in agent.capabilities}

    assert {"filesystem", "shell", "skills", "memory"} <= set(by_type)
    memory = by_type["memory"]
    assert isinstance(memory, Memory)
    assert memory.layout == MemoryLayoutConfig(memories_dir="memories", sessions_dir="sessions")
    assert memory.read == MemoryReadConfig(live_update=True)
    assert isinstance(memory.generate, MemoryGenerateConfig)
    assert memory.generate.phase_one_model == agent.model
    assert memory.generate.phase_two_model == agent.model
    assert "smallest fixes" in memory.generate.extra_prompt
