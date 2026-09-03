import base64
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

from agents import MessageOutputItem, ToolCallItem
from openai.types.responses import ResponseCodeInterpreterToolCall, ResponseOutputMessage

from artifacts import download_artifacts, select_artifacts
from run_reference import build_agent

# Tiny PNG test fixture, not a chart and never shipped as a generated lab result.
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1cAAAAASUVORK5CYII="
)
TOTALS = b"month,revenue_eur\n2025-01,4020.00\n"


def citation(file_id="cfile_chart", filename="monthly_revenue.png", container_id="cntr_test"):
    return {"type": "container_file_citation", "file_id": file_id, "filename": filename,
            "container_id": container_id, "start_index": 0, "end_index": 0}


def example_result(annotations=None, *, status="completed"):
    agent = build_agent("cntr_test")
    if annotations is None:
        annotations = [citation(), citation("cfile_totals", "monthly_totals.csv")]
    call = ResponseCodeInterpreterToolCall(
        id="ci_test", type="code_interpreter_call", container_id="cntr_test", status=status,
        code="print('offline fixture')", outputs=[{"type": "logs", "logs": "36 input rows"}],
    )
    message = ResponseOutputMessage(
        id="msg_test", type="message", role="assistant", status="completed",
        content=[{"type": "output_text", "text": "Here are the chart and totals.", "annotations": annotations}],
    )
    return SimpleNamespace(
        final_output="Here are the chart and totals.",
        new_items=[ToolCallItem(agent=agent, raw_item=call), MessageOutputItem(agent=agent, raw_item=message)],
        context_wrapper=SimpleNamespace(usage=SimpleNamespace(
            requests=1, input_tokens=100, output_tokens=50, total_tokens=150
        )),
    )


class ArtifactTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.retrieve = AsyncMock(side_effect=[SimpleNamespace(content=PNG), SimpleNamespace(content=TOTALS)])
        self.client = SimpleNamespace(containers=SimpleNamespace(
            files=SimpleNamespace(content=SimpleNamespace(retrieve=self.retrieve))
        ))

    async def test_downloads_use_citation_ids_and_fixed_local_names(self):
        result = example_result([citation(filename="../../escape.png"),
                                 citation("cfile_totals", "/mnt/data/monthly_totals.csv")])
        paths = await download_artifacts(self.client, result, "cntr_test", self.path)
        self.assertEqual([path.name for path in paths], ["monthly_revenue.png", "monthly_totals.csv"])
        self.assertEqual(paths[0].read_bytes(), PNG)
        self.assertEqual(paths[1].read_bytes(), TOTALS)
        self.assertEqual([call.kwargs for call in self.retrieve.await_args_list], [
            {"file_id": "cfile_chart", "container_id": "cntr_test"},
            {"file_id": "cfile_totals", "container_id": "cntr_test"},
        ])

    def test_duplicate_citations_are_deduplicated(self):
        result = example_result([citation(), citation(), citation("cfile_totals", "monthly_totals.csv")])
        self.assertEqual(len(select_artifacts(result, "cntr_test")), 2)

    async def test_wrong_container_is_rejected_before_any_download(self):
        result = example_result([citation(container_id="cntr_other"),
                                 citation("cfile_totals", "monthly_totals.csv")])
        with self.assertRaisesRegex(ValueError, "another container"):
            await download_artifacts(self.client, result, "cntr_test", self.path)
        self.retrieve.assert_not_awaited()

    def test_missing_and_ambiguous_citations_are_errors(self):
        for annotations in ([], [citation()],
                            [citation(), citation("cfile_second", "another.png"),
                             citation("cfile_totals", "monthly_totals.csv")]):
            with self.subTest(annotations=annotations), self.assertRaisesRegex(ValueError, "unique cited"):
                select_artifacts(example_result(annotations), "cntr_test")

    def test_failed_code_call_is_not_presented_as_success(self):
        with self.assertRaisesRegex(ValueError, "No completed"):
            select_artifacts(example_result(status="failed"), "cntr_test")

    async def test_non_png_response_is_rejected(self):
        self.retrieve.side_effect = [SimpleNamespace(content=b"<html>Error</html>")]
        with self.assertRaisesRegex(ValueError, "PNG bytes"):
            await download_artifacts(self.client, example_result(), "cntr_test", self.path)
        self.assertEqual(list(self.path.iterdir()), [])

    async def test_bad_totals_are_rejected_before_final_files_are_saved(self):
        self.retrieve.side_effect = [SimpleNamespace(content=PNG),
                                    SimpleNamespace(content=b"month,revenue_eur\n2025-01,NaN\n")]
        with self.assertRaisesRegex(ValueError, "finite"):
            await download_artifacts(self.client, example_result(), "cntr_test", self.path)
        self.assertEqual(list(self.path.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
