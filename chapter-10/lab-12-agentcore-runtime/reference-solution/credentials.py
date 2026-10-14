"""Local environment key or scoped Secrets Manager lookup; no import-time I/O."""

import json
import os

import boto3
from agents import set_default_openai_key


def load_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key:
        return key
    secret_arn = os.getenv("OPENAI_API_KEY_SECRET_ARN", "").strip()
    if not secret_arn:
        raise RuntimeError("Set OPENAI_API_KEY locally or OPENAI_API_KEY_SECRET_ARN in AWS.")
    response = boto3.client("secretsmanager").get_secret_value(SecretId=secret_arn)
    value = json.loads(response["SecretString"])
    key = value.get("OPENAI_API_KEY") if isinstance(value, dict) else None
    if not isinstance(key, str) or not key.strip():
        raise RuntimeError("The secret must contain a nonempty OPENAI_API_KEY JSON field.")
    return key.strip()


def configure_openai() -> None:
    # Read once at process startup. The SDK client retains the key in memory;
    # the key never enters the container image or CloudFormation template.
    set_default_openai_key(load_api_key(), use_for_tracing=False)
