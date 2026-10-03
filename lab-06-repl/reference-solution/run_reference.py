"""A shopping-list conversation using the SDK's terminal REPL."""

import argparse
import asyncio
import os
from agents import Agent, run_demo_loop


def build_agent() -> Agent:
    return Agent(
        name="shopping_assistant",
        instructions=(
            "Maintain a shopping list using this conversation's history. "
            "Start with an empty list. Add or remove items when asked. "
            "After each change, show the complete updated list. "
            "Do not invent items. If there are no items, say the list is empty. "
            "Keep responses short."
        ),
        model="gpt-6-luna",
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-stream", action="store_true", help="Print each complete reply instead of streaming."
    )
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY", "").strip():
        print("Skipped: set OPENAI_API_KEY to run this interactive demo.")
        return

    print("Shopping-list REPL. Type exit or quit to finish. History resets on restart.")
    await run_demo_loop(build_agent(), stream=not args.no_stream)


if __name__ == "__main__":
    asyncio.run(main())
