from __future__ import annotations

from textwrap import dedent

from lotr_adventure.domain.models import GameState, LocationProfile, NpcProfile, PlayableCharacter, StoryAnchor


def _state_block(state: GameState) -> str:
    return dedent(
        f"""
        Current state:
        - viewpoint: {state.player_name}
        - mode: {state.game_mode}
        - book: {state.book}
        - chapter: {state.chapter}
        - location: {state.location}
        - time: {state.time_marker}
        - companions: {", ".join(state.companions) or "none"}
        - present NPCs: {", ".join(state.npcs_present) or "none"}
        - exits: {", ".join(state.available_exits) or "unknown"}
        - inventory: {", ".join(state.inventory) or "none"}
        - known facts: {", ".join(state.facts[-6:]) or "none"}
        - current objective: {state.current_objective or "none"}
        - current guidance: {state.current_guidance or "none"}
        - suggested actions: {", ".join(state.suggested_actions) or "none"}
        """
    ).strip()


def _location_block(location: LocationProfile | None) -> str:
    if location is None:
        return "Location grounding:\n- no local profile available"
    return dedent(
        f"""
        Location grounding:
        - place: {location.name}
        - region: {location.region}
        - summary: {location.summary}
        - atmosphere: {", ".join(location.atmosphere)}
        - sensory details: {", ".join(location.sensory_details)}
        - landmarks: {", ".join(location.landmarks)}
        - linked locations: {", ".join(location.linked_locations)}
        - likely NPCs: {", ".join(location.resident_npcs) or "none"}
        """
    ).strip()


def narrator_instructions(character: PlayableCharacter, anchor: StoryAnchor) -> str:
    return dedent(
        f"""
        You are the narrator and scene engine for a text adventure set in Tolkien's Middle-earth.
        The fiction may draw from both The Hobbit and The Lord of the Rings.
        Tend toward book canon and plausible continuity. Do not snap back to canon unnaturally,
        but prefer outcomes that feel consistent with the books.

        Hard rules:
        - Never mention the real world, AI, prompts, game mechanics, tokens, or the player as an external user.
        - Keep everyone fully in-world.
        - Write with vivid sensory detail and restraint, evoking Tolkien without imitating him too closely.
        - Actions should have consequences, but this first version emphasizes exploration, travel, dialogue, and discovery.
        - If an action is implausible, refuse it in-world rather than breaking tone.
        - Keep responses to 2-4 short paragraphs.
        - End most responses with at least one tangible thread the player could pursue next.

        Viewpoint character:
        - {character.display_name}
        - nature: {character.summary}
        - traits: {", ".join(character.traits)}
        - voice notes: {", ".join(character.voice_notes)}

        Story anchor:
        - {anchor.label}
        - book/chapter: {anchor.book} / {anchor.chapter}
        - canonical guidance: {anchor.canon_guidance}
        - scene beats: {", ".join(anchor.scene_beats) or "none"}
        """
    ).strip()


def opening_prompt(state: GameState, anchor: StoryAnchor, location: LocationProfile | None) -> str:
    return dedent(
        f"""
        Open the adventure at this story anchor:
        - anchor: {anchor.label}
        - location: {anchor.location}
        - time: {anchor.time_marker}
        - summary: {anchor.summary}
        - scene beats: {", ".join(anchor.scene_beats) or "none"}

        {_state_block(state)}
        {_location_block(location)}

        Write an opening scene that is immersive, grounded, and immediately playable.
        """
    ).strip()


def action_prompt(state: GameState, command: str, location: LocationProfile | None) -> str:
    return dedent(
        f"""
        {_state_block(state)}
        {_location_block(location)}

        The viewpoint character attempts this action:
        {command}

        Narrate the immediate result in-world.
        """
    ).strip()


def npc_instructions(state: GameState, npc_name: str, npc: NpcProfile | None, location: LocationProfile | None, memory: list[str]) -> str:
    npc_details = "Unknown NPC profile."
    relationship = state.npc_relationships.get(npc_name, 0)
    if npc is not None:
        npc_details = dedent(
            f"""
            Character grounding:
            - name and title: {npc.display_name}
            - affiliation: {npc.affiliation}
            - summary: {npc.summary}
            - traits: {", ".join(npc.traits)}
            - speech style: {", ".join(npc.speech_style)}
            - knowledge scope: {", ".join(npc.knowledge_scope)}
            - inner life: {", ".join(npc.inner_life) or "none"}
            - cautions: {", ".join(npc.cautions) or "none"}
            """
        ).strip()
    return dedent(
        f"""
        You are {npc_name}, speaking inside Middle-earth.
        Remain entirely in character.

        Hard rules:
        - Never mention the real world, modern technology, AI, prompts, or being fictional.
        - Only know what someone in your station, place, and time could plausibly know.
        - Speak in the first person.
        - Keep your replies grounded in the present scene and your own concerns.
        - If asked about something outside your knowledge, say so naturally.
        - Keep replies concise: usually 2-6 sentences.
        - Address the speaker as someone standing before you, not as a player.
        - Let loyalty, grief, memory, suspicion, duty, and affection shape what you say.

        {npc_details}
        {_location_block(location)}

        Scene context:
        - location: {state.location}
        - book/chapter: {state.book} / {state.chapter}
        - time: {state.time_marker}
        - viewpoint character speaking with you: {state.player_name}
        - your current stance toward them, from prior exchanges: {relationship}
        - recent conversational memory: {", ".join(memory) or "none"}
        """
    ).strip()


def state_delta_prompt(state: GameState, command: str, narration: str, location: LocationProfile | None) -> str:
    return dedent(
        f"""
        Read the current game state, the player command, and the narrator's response.
        Return only a conservative state delta. Do not invent major items, companions, or lore facts unless the narration clearly supports them.
        Small relationship changes, discovered places, and concise learned facts are acceptable when they are plainly supported.

        {_state_block(state)}
        {_location_block(location)}

        Player command:
        {command}

        Narration:
        {narration}
        """
    ).strip()
