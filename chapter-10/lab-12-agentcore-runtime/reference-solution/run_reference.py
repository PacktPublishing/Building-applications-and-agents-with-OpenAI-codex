"""Local single invocation; CloudWatch export is configured in the AWS runtime."""

import argparse
import asyncio
import json
import os
import uuid

from dotenv import load_dotenv


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default="What does the observability course cover?")
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY_SECRET_ARN"):
        print("SKIP: OPENAI_API_KEY is absent; no model call or AWS lookup was made.")
        return 0

    from credentials import configure_openai
    from telemetry import instrument_agents
    from runtime_app import invoke
    from bedrock_agentcore.runtime.context import RequestContext

    instrument_agents()
    configure_openai()
    result = asyncio.run(invoke({"prompt": args.prompt}, RequestContext(session_id=str(uuid.uuid4()))))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
