"""Local smoke check for manifest path validation; makes no API calls."""

from sandbox_manifest import build_manifest
from run_sandbox_demo import build_agent


def main() -> None:
    manifest = build_manifest()
    entries = manifest.validated_entries()
    expected = {"repo", "skills/debug-failing-tests", "memories"}
    assert set(entries) == expected, f"Unexpected manifest destinations: {set(entries)!r}"
    assert all(not str(path).startswith("/") for path in entries), "Manifest paths must be relative"
    memory_files = entries["memories"].children
    assert set(memory_files) == {"MEMORY.md", "memory_summary.md"}
    assert all(file.content for file in memory_files.values()), "Seeded memory files must not be empty"

    capability_types = {capability.type for capability in build_agent().capabilities}
    assert "memory" in capability_types, "SandboxAgent must expose the Memory capability"
    print("Manifest and seeded memory validated; SandboxAgent exposes Memory.")


if __name__ == "__main__":
    main()
