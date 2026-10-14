import contextlib
import io
import os
import unittest
from unittest.mock import AsyncMock, patch

from agents import Agent

from run_reference import build_agent, main


class ReplTests(unittest.IsolatedAsyncioTestCase):
    def test_real_agent_uses_gpt_6_luna(self):
        agent = build_agent()
        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.model, "gpt-6-luna")

    def test_model_is_explicit(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(build_agent().model, "gpt-6-luna")

    async def test_stream_modes(self):
        for flags, expected in [([], True), (["--no-stream"], False)]:
            with self.subTest(flags=flags):
                with (
                    patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-key"}),
                    patch("sys.argv", ["run_reference.py", *flags]),
                    patch("run_reference.run_demo_loop", new_callable=AsyncMock) as loop,
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    await main()
                loop.assert_awaited_once()
                self.assertIsInstance(loop.await_args.args[0], Agent)
                self.assertEqual(loop.await_args.kwargs, {"stream": expected})

    async def test_missing_or_blank_key_skips(self):
        for environment in [{}, {"OPENAI_API_KEY": "  "}]:
            with self.subTest(environment=environment):
                output = io.StringIO()
                with (
                    patch.dict(os.environ, environment, clear=True),
                    patch("sys.argv", ["run_reference.py"]),
                    patch("run_reference.run_demo_loop", new_callable=AsyncMock) as loop,
                    contextlib.redirect_stdout(output),
                ):
                    await main()
                loop.assert_not_called()
                self.assertIn("Skipped:", output.getvalue())


if __name__ == "__main__":
    unittest.main()
