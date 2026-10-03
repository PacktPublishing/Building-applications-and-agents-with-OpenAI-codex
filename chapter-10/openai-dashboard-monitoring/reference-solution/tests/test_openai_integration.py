import os

import pytest

from run_reference import main


@pytest.mark.asyncio
async def test_two_grouped_runs_reach_openai():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is not set")
    assert await main() == 0
