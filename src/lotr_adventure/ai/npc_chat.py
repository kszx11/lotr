from __future__ import annotations

from lotr_adventure.ai.client import OpenAIClient
from lotr_adventure.ai.prompts import npc_instructions
from lotr_adventure.domain.models import GameState, LocationProfile, NpcProfile


class NpcChatEngine:
    def __init__(self, client: OpenAIClient) -> None:
        self.client = client

    def reply(
        self,
        state: GameState,
        npc_name: str,
        player_line: str,
        npc_profile: NpcProfile | None,
        location: LocationProfile | None,
    ) -> str:
        history = state.npc_threads.setdefault(npc_name, [])
        memory = state.npc_memories.setdefault(npc_name, [])
        instructions = npc_instructions(state, npc_name, npc_profile, location, memory[-4:])
        guarded_reply = self._answer_about_present_player(state, npc_name, player_line)
        if guarded_reply is not None:
            reply = guarded_reply
        else:
            try:
                reply = self.client.text(instructions=instructions, history=history, prompt=player_line)
            except Exception:
                reply = self._fallback_reply(npc_name, player_line, npc_profile, location)
        history.append({"role": "user", "content": player_line})
        history.append({"role": "assistant", "content": reply})
        state.npc_threads[npc_name] = history[-12:]
        self._update_memory(state, npc_name, player_line, reply)
        return reply

    @staticmethod
    def _update_memory(state: GameState, npc_name: str, player_line: str, reply: str) -> None:
        memory = state.npc_memories.setdefault(npc_name, [])
        player_note = player_line.strip()
        if player_note:
            memory.append(f"Player raised: {player_note[:80]}")
        if reply:
            memory.append(f"{npc_name} answered: {reply[:100]}")
        state.npc_memories[npc_name] = memory[-6:]
        state.npc_relationships[npc_name] = state.npc_relationships.get(npc_name, 0) + 1

    @staticmethod
    def _fallback_reply(
        npc_name: str,
        player_line: str,
        npc_profile: NpcProfile | None,
        location: LocationProfile | None,
    ) -> str:
        lowered = player_line.lower()
        if npc_profile is None:
            return f"{npc_name} regards you carefully. \"These are grave days, and I will say no more than prudence allows.\""
        if "who" in lowered or "name" in lowered:
            return (
                f"\"I am {npc_profile.display_name},\" {npc_name} says. "
                f"\"I stand with {npc_profile.affiliation}, and these days ask much of us all.\""
            )
        if "where" in lowered or "road" in lowered or "way" in lowered:
            place = location.name if location is not None else "this place"
            return (
                f"\"This is {place}, and the roads about it are not to be taken lightly,\" "
                f"{npc_name} says."
            )
        if "why" in lowered or "fear" in lowered or "danger" in lowered:
            caution = npc_profile.cautions[0] if npc_profile.cautions else "caution"
            return f"\"There is danger enough here, and {caution} is no empty habit,\" {npc_name} says."
        if "how are you" in lowered or "how fare" in lowered or "what troubles you" in lowered:
            inner = npc_profile.inner_life[0] if npc_profile.inner_life else npc_profile.summary
            return f"\"I bear {inner},\" {npc_name} says, after a moment. \"Yet there is work to do before comfort may be claimed.\""
        knowledge = npc_profile.knowledge_scope[0] if npc_profile.knowledge_scope else "the matters before us"
        return (
            f"\"I can speak of {knowledge}, if that is your wish,\" {npc_name} says. "
            f"\"But some things are better weighed carefully before they are spoken aloud.\""
        )

    @staticmethod
    def _answer_about_present_player(state: GameState, npc_name: str, player_line: str) -> str | None:
        lowered = player_line.strip().lower()
        player_name = state.player_name.split(",", 1)[0].strip()
        player_name_lower = player_name.lower()
        asks_where = any(phrase in lowered for phrase in ("where is ", "where's ", "where art ", "where stands "))
        asks_who = any(phrase in lowered for phrase in ("who is ", "who's "))
        if player_name_lower not in lowered:
            return None
        if asks_where:
            return f"\"{player_name} stands before me now,\" {npc_name} says."
        if asks_who:
            return f"\"{player_name} is the one who stands before me now,\" {npc_name} says."
        return None
