"""Create a dedicated lab secret without placing the key in shell history."""

import argparse
import getpass
import json
import os

import boto3
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", required=True)
    parser.add_argument("--name", default="lab12/openai-api-key")
    args = parser.parse_args()
    key = (os.getenv("OPENAI_API_KEY") or getpass.getpass("OpenAI API key: ")).strip()
    if not key:
        raise SystemExit("A nonempty key is required.")
    result = boto3.client("secretsmanager", region_name=args.region).create_secret(
        Name=args.name, Description="Dedicated Chapter 10 Lab 12 OpenAI key",
        SecretString=json.dumps({"OPENAI_API_KEY": key}),
    )
    print(result["ARN"])


if __name__ == "__main__":
    main()
