"""Files API and vector store lifecycle; no agent execution lives here."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Literal

from openai import AsyncOpenAI, NotFoundError
from pydantic import BaseModel, ConfigDict, Field

DATA_DIR = Path(__file__).resolve().parent / "data"
CATEGORIES = ("delivery", "returns", "support")
DEFAULT_STATE = Path(__file__).resolve().parent / ".vector-store-state.json"


class StoreState(BaseModel):
    """Only resources created by this lab, retained until cleanup succeeds."""

    model_config = ConfigDict(extra="forbid", strict=True)
    version: Literal[1] = 1
    vector_store_id: Annotated[str, Field(pattern=r"^vs_[A-Za-z0-9_-]+$")] | None = None
    file_ids: list[Annotated[str, Field(pattern=r"^file[-_][A-Za-z0-9_-]+$")]] = Field(
        default_factory=list
    )
    ready: bool = False


def save_state(path: Path, state: StoreState) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(state.model_dump_json(indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_state(path: Path) -> StoreState:
    if not path.exists():
        raise ValueError(f"No resource manifest at {path}. Run ingest first.")
    return StoreState.model_validate_json(path.read_text(encoding="utf-8"))


def ready_store_id(path: Path) -> str:
    state = load_state(path)
    if not state.ready or not state.vector_store_id or len(state.file_ids) != 3:
        raise ValueError("Ingestion is incomplete. Run cleanup, then ingest again.")
    return state.vector_store_id


async def ingest(
    client: AsyncOpenAI, path: Path, *, poll_timeout: float = 120
) -> StoreState:
    documents = [DATA_DIR / f"{category}.md" for category in CATEGORIES]
    if not all(document.is_file() for document in documents):
        raise ValueError("The three bundled data/*.md documents are required.")
    state = StoreState()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Reserve before making remote changes. A second ingest must never overwrite IDs.
    try:
        with path.open("x", encoding="utf-8") as manifest:
            manifest.write(state.model_dump_json(indent=2) + "\n")
    except FileExistsError as exc:
        raise ValueError(f"Resource manifest already exists at {path}. Run cleanup first.") from exc

    vector_store = await client.vector_stores.create(
        name="Lab 07 - Northstar Market",
        metadata={"lab": "07-vector-store"},
        expires_after={"anchor": "last_active_at", "days": 1},
    )
    state.vector_store_id = vector_store.id
    print(f"Created vector store: {vector_store.id}", flush=True)
    save_state(path, state)

    for document in documents:
        with document.open("rb") as content:
            uploaded = await client.files.create(file=content, purpose="assistants")
        state.file_ids.append(uploaded.id)
        print(f"Uploaded {document.name}: {uploaded.id}", flush=True)
        save_state(path, state)
        indexed = await asyncio.wait_for(
            client.vector_stores.files.create_and_poll(
                vector_store_id=vector_store.id,
                file_id=uploaded.id,
                attributes={"category": document.stem},
                poll_interval_ms=1000,
            ),
            timeout=poll_timeout,
        )
        # The SDK poll helper also returns failed/cancelled files, not just successes.
        if indexed.status != "completed":
            raise RuntimeError(
                f"Indexing {document.name}: {indexed.status}; {indexed.last_error}. "
                "Run cleanup before retrying ingestion."
            )
        print(f"Indexed {document.name}: completed", flush=True)

    state.ready = True
    save_state(path, state)
    print(f"Ready. Reuse this store with search and ask. Manifest: {path}")
    return state


async def cleanup(client: AsyncOpenAI, path: Path) -> None:
    if not path.exists():
        print("No manifest; nothing to clean up.")
        return
    state = load_state(path)
    state.ready = False
    save_state(path, state)
    if state.vector_store_id:
        try:
            result = await client.vector_stores.delete(state.vector_store_id)
            if not result.deleted:
                raise RuntimeError("Vector store deletion was not confirmed; retry cleanup.")
        except NotFoundError:
            pass  # Includes a store that has already expired or been removed.
        print(f"Removed vector store: {state.vector_store_id}", flush=True)
        state.vector_store_id = None
        save_state(path, state)
    # Deleting a vector store does not delete the original Files API objects.
    for file_id in list(state.file_ids):
        try:
            result = await client.files.delete(file_id)
            if not result.deleted:
                raise RuntimeError(f"Deletion of {file_id} was not confirmed; retry cleanup.")
        except NotFoundError:
            pass
        print(f"Removed uploaded file: {file_id}", flush=True)
        state.file_ids.remove(file_id)
        save_state(path, state)
    path.unlink()
    print("Cleanup complete; resource manifest removed.")
