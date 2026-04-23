from __future__ import annotations

from lotr_adventure.ai.client import OpenAIClient
from lotr_adventure.ai.prompts import action_prompt, narrator_instructions, opening_prompt
from lotr_adventure.domain.models import GameState, LocationProfile, PlayableCharacter, StoryAnchor


class NarratorEngine:
    def __init__(self, client: OpenAIClient) -> None:
        self.client = client

    def opening_scene(
        self,
        state: GameState,
        character: PlayableCharacter,
        anchor: StoryAnchor,
        location: LocationProfile | None,
    ) -> str:
        instructions = narrator_instructions(character, anchor)
        prompt = opening_prompt(state, anchor, location)
        try:
            return self.client.text(instructions=instructions, history=state.narrator_history, prompt=prompt)
        except Exception:
            local_mood = ""
            if location is not None and location.sensory_details:
                local_mood = f" About you are {location.sensory_details[0].lower()}."
            return (
                f"The tale opens in {state.location}, where {state.player_name} stands beneath the weight of {state.book}. "
                f"The hour is {state.time_marker}, and the air itself seems to listen.{local_mood} "
                f"Roads, voices, and hidden purposes lie near at hand."
            )

    def narrate_action(
        self,
        state: GameState,
        character: PlayableCharacter,
        anchor: StoryAnchor,
        command: str,
        location: LocationProfile | None,
    ) -> str:
        instructions = narrator_instructions(character, anchor)
        prompt = action_prompt(state, command, location)
        try:
            return self.client.text(instructions=instructions, history=state.narrator_history, prompt=prompt)
        except Exception:
            if command.lower().startswith(("go ", "go to ", "travel ", "travel to ", "move to ", "head to ")):
                if "no known road or path" in command.lower():
                    return (
                        "You find no ready road that answers the wish. The land about you offers other ways, "
                        "but not that one, not from where you now stand."
                    )
                return f"You set out from {state.location}, and the road yields slowly to your purpose. The land changes by degrees as you press on."
            if command.lower().startswith(("inspect ", "examine ", "look at ")):
                detail = ""
                if location is not None and location.landmarks:
                    detail = f" Nearby, {location.landmarks[0].lower()} lingers in your thought."
                return f"You study the matter closely and glean what you can from shape, scent, and memory.{detail}"
            if location is not None and location.atmosphere:
                return (
                    f"For a brief while, the world answers in silence; yet {location.atmosphere[0].lower()} "
                    f"still lies upon {state.location}, and the scene remains tense with possibility."
                )
            return "For a brief while, the world answers in silence; yet the scene remains tense with possibility."
