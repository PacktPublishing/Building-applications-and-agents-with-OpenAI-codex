import contextlib
import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from agents import Agent, FileSearchTool, MessageOutputItem, RunConfig, ToolCallItem
from openai import AsyncOpenAI, AuthenticationError
from openai.types.responses import ResponseFileSearchToolCall, ResponseOutputMessage
from openai.types.vector_store_search_response import VectorStoreSearchResponse
import httpx

import run_reference as app
from store import save_state, StoreState


def example_result():
    agent = app.build_agent("vs_test")
    call = ResponseFileSearchToolCall(
        id="fs_test", type="file_search_call", status="completed", queries=["returns"],
        results=[{"file_id": "file-test", "filename": "returns.md", "score": 0.9,
                  "text": "Unopened coffee may be returned within 14 calendar days."}],
    )
    message = ResponseOutputMessage(
        id="msg_test", type="message", role="assistant", status="completed",
        content=[{"type": "output_text", "text": "Return it within 14 calendar days.",
                  "annotations": [{"type": "file_citation", "file_id": "file-test",
                                   "filename": "returns.md", "index": 0}]}],
    )
    return SimpleNamespace(
        final_output="Return it within 14 calendar days.",
        new_items=[ToolCallItem(agent=agent, raw_item=call),
                   MessageOutputItem(agent=agent, raw_item=message)],
        context_wrapper=SimpleNamespace(usage=SimpleNamespace(
            requests=1, input_tokens=100, output_tokens=20, total_tokens=120
        )),
    )


class AgentContractTests(unittest.TestCase):
    def test_agent_uses_hosted_tool_and_matching_filter(self):
        agent = app.build_agent("vs_test", max_results=2, category="returns")
        self.assertIsInstance(agent, Agent)
        self.assertEqual(len(agent.tools), 1)
        tool = agent.tools[0]
        self.assertIsInstance(tool, FileSearchTool)
        self.assertEqual(tool.vector_store_ids, ["vs_test"])
        self.assertEqual(tool.max_num_results, 2)
        self.assertTrue(tool.include_search_results)
        self.assertEqual(tool.filters, {"type": "eq", "key": "category", "value": "returns"})
        self.assertEqual(agent.model_settings.tool_choice, "required")

    def test_model_override_and_sdk_default(self):
        with patch.dict(os.environ, {"OPENAI_MODEL": "test-model"}):
            self.assertEqual(app.build_agent("vs_test").model, "test-model")
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(app.build_agent("vs_test").model)

    def test_invalid_filters_and_result_limits_are_rejected(self):
        for count in (0, 11):
            with self.assertRaises(ValueError):
                app.build_agent("vs_test", max_results=count)
        with self.assertRaises(ValueError):
            app.build_agent("vs_test", category="unknown")

    def test_results_expose_real_annotations_and_usage(self):
        result = example_result()
        self.assertEqual(app.file_citations(result), [("file-test", "returns.md")])
        self.assertEqual(app.search_calls(result)[0].status, "completed")
        with contextlib.redirect_stdout(io.StringIO()) as output:
            app.print_agent_result(result)
        self.assertIn("file-test", output.getvalue())
        self.assertIn("total_tokens=120", output.getvalue())
        self.assertIn("retrieval score=0.9", output.getvalue())

    def test_missing_results_or_citations_are_not_fabricated(self):
        result = example_result()
        result.new_items[0].raw_item.results = None
        result.new_items[1].raw_item.content[0].annotations = []
        self.assertEqual(app.file_citations(result), [])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            app.print_agent_result(result)
        self.assertIn("None returned", output.getvalue())


class CliTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.enterContext(contextlib.redirect_stdout(self.output))
        self.enterContext(contextlib.redirect_stderr(self.output))
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "state.json"

    async def test_all_commands_skip_without_client_when_key_missing_or_blank(self):
        for key in (None, "", "   "):
            environment = {} if key is None else {"OPENAI_API_KEY": key}
            with patch.dict(os.environ, environment, clear=True), patch.object(app, "AsyncOpenAI") as client:
                for command in (["ingest"], ["search", "returns"], ["ask", "returns"], ["cleanup"]):
                    with self.subTest(key=repr(key), command=command):
                        code = await app.main(["--state", str(self.path), *command])
                        self.assertEqual(code, 0)
                client.assert_not_called()
        self.assertFalse(self.path.exists())
        self.assertIn("SKIP:", self.output.getvalue())

    async def test_help_needs_no_client(self):
        with patch.object(app, "AsyncOpenAI") as client, self.assertRaises(SystemExit) as stopped:
            await app.main(["--help"])
        self.assertEqual(stopped.exception.code, 0)
        client.assert_not_called()

    async def test_run_config_uses_responses_provider_and_trace_metadata(self):
        async with AsyncOpenAI(api_key="dummy-offline") as client:
            config = app.build_run_config(client)
            self.assertIsInstance(config, RunConfig)
            self.assertEqual(config.workflow_name, "lab-07-vector-store")
            self.assertEqual(config.trace_metadata["lab"], "07")
            self.assertFalse(config.trace_include_sensitive_data)
            from agents.models.openai_responses import OpenAIResponsesModel
            self.assertIsInstance(config.model_provider.get_model(None), OpenAIResponsesModel)

    async def test_search_passes_filter_and_prints_raw_chunks(self):
        save_state(self.path, StoreState(vector_store_id="vs_test", ready=True,
                                        file_ids=["file-0", "file-1", "file-2"]))
        hit = VectorStoreSearchResponse(
            file_id="file-1", filename="returns.md", score=0.7,
            attributes={"category": "returns"},
            content=[{"type": "text", "text": "14 calendar days"}],
        )
        client = SimpleNamespace(vector_stores=SimpleNamespace(
            search=AsyncMock(return_value=SimpleNamespace(data=[hit]))
        ))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-offline"}), patch.object(app, "AsyncOpenAI") as constructor:
            constructor.return_value.__aenter__ = AsyncMock(return_value=client)
            constructor.return_value.__aexit__ = AsyncMock(return_value=False)
            code = await app.main(["--state", str(self.path), "search", "return coffee",
                                   "--category", "returns", "--max-results", "2"])
        self.assertEqual(code, 0)
        client.vector_stores.search.assert_awaited_once_with(
            vector_store_id="vs_test", query="return coffee", max_num_results=2,
            filters={"type": "eq", "key": "category", "value": "returns"},
        )
        self.assertIn("14 calendar days", self.output.getvalue())

    async def test_ask_passes_real_agent_and_run_config_to_runner(self):
        save_state(self.path, StoreState(vector_store_id="vs_test", ready=True,
                                        file_ids=["file-0", "file-1", "file-2"]))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-offline"}), \
                patch.object(app.Runner, "run", new=AsyncMock(return_value=example_result())) as run:
            code = await app.main(["--state", str(self.path), "ask", "return coffee"])
        self.assertEqual(code, 0)
        self.assertIsInstance(run.call_args.args[0], Agent)
        self.assertEqual(run.call_args.args[1], "return coffee")
        self.assertIsInstance(run.call_args.kwargs["run_config"], RunConfig)
        self.assertEqual(run.call_args.kwargs["max_turns"], 5)

    async def test_incomplete_state_does_not_reach_runner(self):
        save_state(self.path, StoreState(vector_store_id="vs_test"))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-offline"}), \
                patch.object(app.Runner, "run", new=AsyncMock()) as run:
            self.assertEqual(await app.main(["--state", str(self.path), "ask", "returns"]), 1)
        run.assert_not_awaited()

    async def test_authentication_error_body_is_not_printed(self):
        secret = "dummy-secret-that-must-not-appear"
        error = AuthenticationError(
            f"Incorrect API key: {secret}",
            response=httpx.Response(401, request=httpx.Request("POST", "https://example.com")),
            body=None,
        )
        with patch.dict(os.environ, {"OPENAI_API_KEY": secret}), \
                patch.object(app, "ingest", new=AsyncMock(side_effect=error)):
            self.assertEqual(await app.main(["--state", str(self.path), "ingest"]), 1)
        self.assertIn("AuthenticationError", self.output.getvalue())
        self.assertNotIn(secret, self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
