from __future__ import annotations

import json

from openai import OpenAI

from lotr_adventure.config import Config


class OpenAIClient:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = OpenAI(api_key=config.api_key) if config.api_key else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def text(self, *, instructions: str, history: list[dict[str, str]], prompt: str, model: str | None = None) -> str:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        response = self.client.responses.create(
            model=model or self.config.text_model,
            instructions=instructions,
            input=[*history, {"role": "user", "content": prompt}],
            store=False,
        )
        return response.output_text.strip()

    def structured(self, *, instructions: str, prompt: str, schema_name: str, schema: dict, model: str | None = None) -> dict:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        response = self.client.responses.create(
            model=model or self.config.structured_model,
            instructions=instructions,
            input=[{"role": "user", "content": prompt}],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": schema,
                    "strict": True,
                }
            },
            store=False,
        )
        return json.loads(response.output_text)
