from __future__ import annotations

from lotr_adventure.ai.client import OpenAIClient
from lotr_adventure.ai.prompts import state_delta_prompt
from lotr_adventure.ai.schemas import STATE_DELTA_SCHEMA, StateDelta
from lotr_adventure.domain.models import GameState, LocationProfile


class StateUpdateEngine:
    def __init__(self, client: OpenAIClient) -> None:
        self.client = client

    def generate(self, state: GameState, command: str, narration: str, location: LocationProfile | None) -> StateDelta:
        prompt = state_delta_prompt(state, command, narration, location)
        instructions = (
            "You produce strict JSON state deltas for a Middle-earth adventure game. "
            "Stay conservative and grounded in the narration."
        )
        try:
            payload = self.client.structured(
                instructions=instructions,
                prompt=prompt,
                schema_name="state_delta",
                schema=STATE_DELTA_SCHEMA,
            )
            return StateDelta.model_validate(payload)
        except Exception:
            return StateDelta()
