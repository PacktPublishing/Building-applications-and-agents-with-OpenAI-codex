import contextlib
import io
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from agents import Agent, CodeInterpreterTool, RunConfig
import httpx
from openai import AsyncOpenAI, NotFoundError

import run_reference as app
from resources import Resources, cleanup, save_resources
from test_artifacts import PNG, TOTALS, example_result


def mock_client():
    client = MagicMock()
    client.files.create = AsyncMock(return_value=SimpleNamespace(id="file-test"))
    client.containers.create = AsyncMock(return_value=SimpleNamespace(id="cntr_test"))
    client.containers.files.content.retrieve = AsyncMock(
        side_effect=[SimpleNamespace(content=PNG), SimpleNamespace(content=TOTALS)]
    )
    client.containers.delete = AsyncMock(return_value=None)
    client.files.delete = AsyncMock(return_value=SimpleNamespace(deleted=True))
    return client


class RunnerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.output = io.StringIO()
        self.enterContext(contextlib.redirect_stdout(self.output))
        self.enterContext(contextlib.redirect_stderr(self.output))

    async def test_agent_and_config_keep_sdk_objects_visible(self):
        agent = app.build_agent("cntr_test")
        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.model, "gpt-6-luna")
        self.assertEqual(len(agent.tools), 1)
        self.assertIsInstance(agent.tools[0], CodeInterpreterTool)
        self.assertEqual(agent.tools[0].tool_config,
                         {"type": "code_interpreter", "container": "cntr_test"})
        self.assertEqual(agent.model_settings.tool_choice, "required")
        self.assertIn("code_interpreter_call.outputs", agent.model_settings.response_include)
        async with AsyncOpenAI(api_key="dummy-offline") as client:
            config = app.build_run_config(client)
            self.assertIsInstance(config, RunConfig)
            self.assertEqual(config.workflow_name, "lab-08-code-interpreter")
            self.assertEqual(config.trace_metadata["lab"], "08")
            self.assertFalse(config.trace_include_sensitive_data)
            from agents.models.openai_responses import OpenAIResponsesModel
            self.assertIsInstance(config.model_provider.get_model(None), OpenAIResponsesModel)

    async def test_missing_or_blank_key_skips_both_commands_without_side_effects(self):
        for value in (None, "", "   "):
            environment = {} if value is None else {"OPENAI_API_KEY": value}
            with patch.dict(os.environ, environment, clear=True), patch.object(app, "AsyncOpenAI") as client:
                self.assertEqual(await app.main(["run", "--output-dir", str(self.path / "out")]), 0)
                self.assertEqual(await app.main(["cleanup", "--run-dir", str(self.path)]), 0)
                client.assert_not_called()
        self.assertFalse((self.path / "out").exists())
        self.assertIn("SKIP", self.output.getvalue())

    async def test_help_needs_no_client(self):
        with patch.object(app, "AsyncOpenAI") as client, self.assertRaises(SystemExit) as stopped:
            await app.main(["--help"])
        self.assertEqual(stopped.exception.code, 0)
        client.assert_not_called()

    async def test_invalid_csv_stops_before_client_creation(self):
        path = self.path / "bad.csv"
        path.write_text("wrong,columns\n1,2\n")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-offline"}), patch.object(app, "AsyncOpenAI") as client:
            self.assertEqual(await app.main(["run", "--csv", str(path)]), 1)
            client.assert_not_called()

    async def test_cleanup_retries_only_remaining_resource(self):
        save_resources(self.path, Resources(uploaded_file_id="file-test", container_id="cntr_test"))
        chart = self.path / "monthly_revenue.png"
        chart.write_bytes(b"preserved-local-test-artifact")
        client = SimpleNamespace(containers=SimpleNamespace(delete=AsyncMock(return_value=None)),
                                 files=SimpleNamespace(delete=AsyncMock(side_effect=RuntimeError("retry"))))
        with self.assertRaisesRegex(RuntimeError, "retry"):
            await cleanup(client, self.path)
        remaining = Resources.model_validate_json((self.path / "resources.json").read_text())
        self.assertIsNone(remaining.container_id)
        self.assertEqual(remaining.uploaded_file_id, "file-test")
        client.files.delete.side_effect = None
        client.files.delete.return_value = SimpleNamespace(deleted=True)
        await cleanup(client, self.path)
        client.containers.delete.assert_awaited_once_with("cntr_test")
        self.assertFalse((self.path / "resources.json").exists())
        self.assertTrue(chart.exists())

    async def test_cleanup_handles_expired_or_deleted_resources(self):
        save_resources(self.path, Resources(uploaded_file_id="file-test", container_id="cntr_test"))
        missing = NotFoundError("gone", body=None,
                               response=httpx.Response(404, request=httpx.Request("DELETE", "https://example.com")))
        client = SimpleNamespace(containers=SimpleNamespace(delete=AsyncMock(side_effect=missing)),
                                 files=SimpleNamespace(delete=AsyncMock(side_effect=missing)))
        await cleanup(client, self.path)
        self.assertFalse((self.path / "resources.json").exists())

    async def test_full_mocked_run_downloads_before_cleanup(self):
        client = mock_client()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-offline"}), \
                patch.object(app, "AsyncOpenAI") as constructor, \
                patch.object(app.Runner, "run", new=AsyncMock(return_value=example_result())) as run:
            constructor.return_value.__aenter__ = AsyncMock(return_value=client)
            constructor.return_value.__aexit__ = AsyncMock(return_value=False)
            code = await app.main(["run", "--output-dir", str(self.path)])
        self.assertEqual(code, 0, self.output.getvalue())
        folder = next(self.path.glob("run-*"))
        self.assertEqual((folder / "monthly_revenue.png").read_bytes(), PNG)
        self.assertEqual((folder / "monthly_totals.csv").read_bytes(), TOTALS)
        report = json.loads((folder / "run-report.json").read_text())
        self.assertEqual(report["input_rows"], 36)
        self.assertEqual(report["code_interpreter_calls"][0]["status"], "completed")
        self.assertFalse((folder / "resources.json").exists())
        self.assertIsInstance(run.call_args.args[0], Agent)
        self.assertIsInstance(run.call_args.kwargs["run_config"], RunConfig)
        self.assertEqual(client.files.create.call_args.kwargs["purpose"], "user_data")
        self.assertEqual(client.containers.create.call_args.kwargs["file_ids"], ["file-test"])
        self.assertEqual(client.containers.create.call_args.kwargs["memory_limit"], "1g")
        calls = [call[0] for call in client.mock_calls]
        self.assertLess(max(i for i, name in enumerate(calls) if name == "containers.files.content.retrieve"),
                        calls.index("containers.delete"))
        client.containers.delete.assert_awaited_once_with("cntr_test")
        client.files.delete.assert_awaited_once_with("file-test")

    async def test_failures_still_clean_up_known_resources(self):
        for stage in ("container", "model", "download"):
            with self.subTest(stage=stage):
                parent = self.path / stage
                client = mock_client()
                run = AsyncMock(return_value=example_result())
                if stage == "container":
                    client.containers.create.side_effect = RuntimeError("container failed")
                elif stage == "model":
                    run.side_effect = RuntimeError("model failed")
                else:
                    client.containers.files.content.retrieve.side_effect = RuntimeError("download failed")
                with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-offline"}), \
                        patch.object(app, "AsyncOpenAI") as constructor, patch.object(app.Runner, "run", new=run):
                    constructor.return_value.__aenter__ = AsyncMock(return_value=client)
                    constructor.return_value.__aexit__ = AsyncMock(return_value=False)
                    self.assertEqual(await app.main(["run", "--output-dir", str(parent)]), 1)
                client.files.delete.assert_awaited_once_with("file-test")
                if stage != "container":
                    client.containers.delete.assert_awaited_once_with("cntr_test")
                else:
                    client.containers.delete.assert_not_awaited()
                folder = next(parent.glob("run-*"))
                self.assertFalse((folder / "resources.json").exists())
                self.assertFalse((folder / "monthly_revenue.png").exists())

    async def test_cleanup_failure_retains_manifest_and_downloads(self):
        client = mock_client()
        client.containers.delete.side_effect = RuntimeError("cleanup failed")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-offline"}), \
                patch.object(app, "AsyncOpenAI") as constructor, \
                patch.object(app.Runner, "run", new=AsyncMock(return_value=example_result())):
            constructor.return_value.__aenter__ = AsyncMock(return_value=client)
            constructor.return_value.__aexit__ = AsyncMock(return_value=False)
            self.assertEqual(await app.main(["run", "--output-dir", str(self.path)]), 1)
        folder = next(self.path.glob("run-*"))
        self.assertTrue((folder / "monthly_revenue.png").exists())
        self.assertTrue((folder / "resources.json").exists())
        self.assertIn("Retry cleanup:", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
