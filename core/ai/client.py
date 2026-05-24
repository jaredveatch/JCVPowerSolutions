import os

from openai import OpenAI


def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    return OpenAI(api_key=api_key)


def get_openai_model():
    return os.environ.get("OPENAI_MODEL", "gpt-5.1")