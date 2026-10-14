"""Track this run's upload and explicit Code Interpreter container."""

from pathlib import Path
from typing import Annotated, Literal

from openai import AsyncOpenAI, NotFoundError
from pydantic import BaseModel, ConfigDict, Field


class Resources(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    version: Literal[1] = 1
    uploaded_file_id: Annotated[str, Field(pattern=r"^file[-_][A-Za-z0-9_-]+$")] | None = None
    container_id: Annotated[str, Field(pattern=r"^cntr_[A-Za-z0-9_-]+$")] | None = None


def save_resources(run_dir: Path, resources: Resources) -> None:
    temporary = run_dir / "resources.json.tmp"
    temporary.write_text(resources.model_dump_json(indent=2) + "\n", encoding="utf-8")
    temporary.replace(run_dir / "resources.json")


async def cleanup(client: AsyncOpenAI, run_dir: Path) -> None:
    manifest = run_dir / "resources.json"
    if not manifest.exists():
        print("No resource manifest; nothing to clean up.")
        return
    state = Resources.model_validate_json(manifest.read_text(encoding="utf-8"))
    if state.container_id:
        try:
            # This endpoint returns None on success, not a deleted boolean object.
            await client.containers.delete(state.container_id)
        except NotFoundError:
            pass
        print(f"Removed container: {state.container_id}", flush=True)
        state.container_id = None
        save_resources(run_dir, state)
    if state.uploaded_file_id:
        try:
            deleted = await client.files.delete(state.uploaded_file_id)
            if not deleted.deleted:
                raise RuntimeError("Upload deletion was not confirmed; retry cleanup.")
        except NotFoundError:
            pass
        print(f"Removed original upload: {state.uploaded_file_id}", flush=True)
        state.uploaded_file_id = None
        save_resources(run_dir, state)
    manifest.unlink()
    print("Remote cleanup complete. Local artifacts are preserved.")
