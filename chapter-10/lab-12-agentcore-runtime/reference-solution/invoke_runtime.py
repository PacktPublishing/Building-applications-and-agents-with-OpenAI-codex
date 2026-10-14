"""SigV4-authenticated invocation; the client needs AWS credentials, not an OpenAI key."""

import argparse
import json
import uuid

import boto3
from botocore.config import Config

from runtime_app import InvocationRequest


def invoke_remote(client, runtime_arn: str, prompt: str, session_id: str) -> dict:
    if not 33 <= len(session_id) <= 256:
        raise ValueError("AgentCore runtime session IDs must be 33–256 characters.")
    request = InvocationRequest(prompt=prompt)
    response = client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn, runtimeSessionId=session_id, qualifier="DEFAULT",
        contentType="application/json", accept="application/json",
        payload=request.model_dump_json().encode("utf-8"),
    )
    body = response["response"]
    try:
        return json.loads(body.read())
    finally:
        body.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-arn", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--session-id", default=str(uuid.uuid4()))
    parser.add_argument("--prompt", default="What does the observability course cover?")
    args = parser.parse_args()
    client = boto3.client("bedrock-agentcore", region_name=args.region,
                          config=Config(read_timeout=180, retries={"max_attempts": 0}))
    print(json.dumps(invoke_remote(client, args.runtime_arn, args.prompt, args.session_id), indent=2))


if __name__ == "__main__":
    main()
