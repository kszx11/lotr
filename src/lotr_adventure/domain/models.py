from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PlayableCharacter:
    id: str
    name: str
    title: str
    summary: str
    traits: list[str]
    voice_notes: list[str]
    starting_inventory: list[str]

    @property
    def display_name(self) -> str:
        return f"{self.name}, {self.title}"


@dataclass
class StoryAnchor:
    id: str
    label: str
    book: str
    chapter: str
    location: str
    time_marker: str
    viewpoint_character_id: str
    summary: str
    canon_guidance: str
    scene_beats: list[str] = field(default_factory=list)
    starting_npcs: list[str] = field(default_factory=list)
    starting_companions: list[str] = field(default_factory=list)
    available_exits: list[str] = field(default_factory=list)


@dataclass
class NpcProfile:
    name: str
    title: str
    affiliation: str
    summary: str
    speech_style: list[str]
    traits: list[str]
    knowledge_scope: list[str]
    inner_life: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return f"{self.name}, {self.title}"


@dataclass
class LocationProfile:
    id: str
    name: str
    region: str
    summary: str
    atmosphere: list[str]
    sensory_details: list[str] = field(default_factory=list)
    landmarks: list[str] = field(default_factory=list)
    resident_npcs: list[str] = field(default_factory=list)
    linked_locations: list[str] = field(default_factory=list)
    travel_keywords: list[str] = field(default_factory=list)


@dataclass
class StoryStep:
    anchor_id: str
    title: str
    objective: str
    guidance: str
    suggested_actions: list[str] = field(default_factory=list)
    required_locations: list[str] = field(default_factory=list)
    required_npcs: list[str] = field(default_factory=list)
    required_inspections: list[str] = field(default_factory=list)
    required_fact_keywords: list[str] = field(default_factory=list)


@dataclass
class StoryPath:
    id: str
    label: str
    character_id: str
    summary: str
    steps: list[StoryStep]


@dataclass
class GameState:
    player_character_id: str
    player_name: str
    game_mode: str
    anchor_id: str
    book: str
    chapter: str
    location: str
    time_marker: str
    story_path_id: str = ""
    story_step_index: int = 0
    unlocked_anchors: list[str] = field(default_factory=list)
    current_objective: str = ""
    current_guidance: str = ""
    suggested_actions: list[str] = field(default_factory=list)
    completed_objectives: list[str] = field(default_factory=list)
    inventory: list[str] = field(default_factory=list)
    companions: list[str] = field(default_factory=list)
    npcs_present: list[str] = field(default_factory=list)
    available_exits: list[str] = field(default_factory=list)
    visited_locations: list[str] = field(default_factory=list)
    location_history: list[str] = field(default_factory=list)
    spoken_to_npcs: list[str] = field(default_factory=list)
    inspected_targets: list[str] = field(default_factory=list)
    journal: list[str] = field(default_factory=list)
    facts: list[str] = field(default_factory=list)
    narrator_history: list[dict[str, str]] = field(default_factory=list)
    npc_threads: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    npc_memories: dict[str, list[str]] = field(default_factory=dict)
    npc_relationships: dict[str, int] = field(default_factory=dict)
    last_narration: str = ""
    mode: str = "exploration"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameState":
        data.setdefault("game_mode", "open")
        data.setdefault("story_path_id", "")
        data.setdefault("story_step_index", 0)
        data.setdefault("unlocked_anchors", [])
        data.setdefault("current_objective", "")
        data.setdefault("current_guidance", "")
        data.setdefault("suggested_actions", [])
        data.setdefault("completed_objectives", [])
        data.setdefault("visited_locations", [])
        data.setdefault("location_history", [])
        data.setdefault("spoken_to_npcs", [])
        data.setdefault("inspected_targets", [])
        data.setdefault("npc_memories", {})
        data.setdefault("npc_relationships", {})
        return cls(**data)


@dataclass
class ParsedCommand:
    kind: str
    raw: str
    target: str | None = None
    topic: str | None = None
