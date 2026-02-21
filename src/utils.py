from uuid import uuid4
import os
from dotenv import load_dotenv

from pydantic_ai.models import ModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel

load_dotenv()


def prefixed_uuid(prefix: str) -> str:
    return f"{prefix}_{uuid4()}"


def model_factory() -> OpenAIChatModel:
    return OpenAIChatModel(
        model_name="gpt-5.2",
        provider=OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")),
        settings=ModelSettings(
            max_tokens=1000,
        )
    )