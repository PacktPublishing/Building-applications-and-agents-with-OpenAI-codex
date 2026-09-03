"""Explicit opt-in only: uploads fictional files and makes a billable model call."""

import os
from pathlib import Path
import tempfile
import unittest

from agents import Runner
from openai import AsyncOpenAI

from run_reference import build_agent, build_run_config, category_filter, file_citations, search_calls
from store import cleanup, ingest


class LiveVectorStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_hosted_retrieval_and_agent_citations(self):
        if os.environ.get("RUN_VECTOR_STORE_SMOKE") != "1":
            self.skipTest("Set RUN_VECTOR_STORE_SMOKE=1 to opt into the live smoke test.")
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            if os.environ.get("REQUIRE_OPENAI_API") == "1":
                self.fail("OPENAI_API_KEY is required for the requested live smoke test.")
            self.skipTest("OPENAI_API_KEY is missing or blank.")

        # Keep this directory if cleanup fails, so its IDs remain recoverable.
        directory = Path(tempfile.mkdtemp(prefix="lab07-vector-store-"))
        path = directory / ".vector-store-state.json"
        print(f"Live smoke resource manifest: {path}", flush=True)
        try:
            async with AsyncOpenAI(api_key=key, timeout=60.0, max_retries=2) as client:
                try:
                    state = await ingest(client, path)
                    results = await client.vector_stores.search(
                        vector_store_id=state.vector_store_id,
                        query="return unopened coffee after 10 days",
                        max_num_results=3,
                        filters=category_filter("returns"),
                    )
                    self.assertTrue(results.data)
                    for hit in results.data:
                        self.assertIn(hit.file_id, state.file_ids)
                        self.assertEqual(hit.attributes["category"], "returns")
                        self.assertTrue(hit.content)

                    agent = build_agent(state.vector_store_id, category="returns")
                    result = await Runner.run(
                        agent, "Can I return unopened coffee 10 days after delivery? Cite the policy.",
                        run_config=build_run_config(client), max_turns=5,
                    )
                    self.assertTrue(str(result.final_output).strip())
                    calls = search_calls(result)
                    self.assertTrue(any(call.status == "completed" and call.results for call in calls))
                    citations = file_citations(result)
                    self.assertTrue(citations, "No file citation annotations were returned.")
                    for file_id, _ in citations:
                        self.assertIn(file_id, state.file_ids)
                finally:
                    await cleanup(client, path)
        finally:
            if path.exists():
                print(f"Cleanup incomplete. Retry with: python run_reference.py --state {path} cleanup",
                      flush=True)
            else:
                directory.rmdir()


if __name__ == "__main__":
    unittest.main()
