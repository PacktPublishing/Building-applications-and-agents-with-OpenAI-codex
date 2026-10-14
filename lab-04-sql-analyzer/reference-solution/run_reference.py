from __future__ import annotations

import argparse
import asyncio
import os

from dotenv import load_dotenv

from sql_analyzer.app import async_main


def require_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required to run this reference demo.")


if __name__ == "__main__":
    # Load .env before require_api_key(); sql_analyzer.app only loads it later.
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run Lab 04 SQL Analyzer Agent demo.")
    parser.add_argument(
        "--question",
        default="Which products generated the most revenue?",
        help="Business question to ask the SQL Analyzer Agent.",
    )
    args = parser.parse_args()
    require_api_key()
    raise SystemExit(asyncio.run(async_main([args.question])))
