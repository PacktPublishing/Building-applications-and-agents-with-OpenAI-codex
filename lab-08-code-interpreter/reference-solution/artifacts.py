"""Download generated artifacts using API citations, never model-written URLs."""

from pathlib import Path, PurePosixPath

from agents import RunResult
from openai import AsyncOpenAI
from openai.types.responses import ResponseCodeInterpreterToolCall, ResponseOutputMessage
from openai.types.responses.response_output_text import AnnotationContainerFileCitation

from csv_checks import validate_rows

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
OUTPUT_NAMES = {".png": "monthly_revenue.png", ".csv": "monthly_totals.csv"}


def select_artifacts(
    result: RunResult, container_id: str
) -> dict[str, AnnotationContainerFileCitation]:
    completed = any(
        isinstance(item.raw_item, ResponseCodeInterpreterToolCall)
        and item.raw_item.status == "completed"
        and item.raw_item.container_id == container_id
        for item in result.new_items
    )
    if not completed:
        raise ValueError("No completed Code Interpreter call for the expected container.")
    candidates = {extension: {} for extension in OUTPUT_NAMES}
    for item in result.new_items:
        if not isinstance(item.raw_item, ResponseOutputMessage):
            continue
        for part in item.raw_item.content:
            if part.type != "output_text":
                continue
            for citation in part.annotations:
                if citation.type != "container_file_citation":
                    continue
                # Names may include container paths. Use only the suffix for selection;
                # remote filenames must never control local write paths.
                extension = PurePosixPath(citation.filename.replace("\\", "/")).suffix.lower()
                if extension not in candidates:
                    continue
                if citation.container_id != container_id:
                    raise ValueError("Generated artifact citation belongs to another container.")
                candidates[extension][citation.file_id] = citation
    selected = {}
    for extension, choices in candidates.items():
        if len(choices) != 1:
            raise ValueError(
                f"Expected one unique cited {extension} artifact, received {len(choices)}. "
                "Inspect run-report.json; rerun and request links to both generated files."
            )
        selected[extension] = next(iter(choices.values()))
    return selected


async def download_artifacts(
    client: AsyncOpenAI, result: RunResult, container_id: str, run_dir: Path
) -> list[Path]:
    selected = select_artifacts(result, container_id)
    payloads = {}
    for extension, citation in selected.items():
        response = await client.containers.files.content.retrieve(
            file_id=citation.file_id, container_id=container_id
        )
        payload = response.content
        if extension == ".png":
            if len(payload) < 33 or not payload.startswith(PNG_SIGNATURE):
                raise ValueError("The cited diagram did not contain PNG bytes.")
        else:
            validate_rows(payload.decode("utf-8-sig"), totals=True)
        payloads[extension] = payload
    # Validate both downloads before saving either final output.
    paths = []
    for extension, payload in payloads.items():
        path = run_dir / OUTPUT_NAMES[extension]
        with path.open("xb") as handle:
            handle.write(payload)
        paths.append(path)
    return paths
