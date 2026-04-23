from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RelationshipDelta(BaseModel):
    npc_name: str
    delta: int


class StateDelta(BaseModel):
    location: Optional[str] = None
    time_marker: Optional[str] = None
    npcs_present: list[str] = Field(default_factory=list)
    companions_present: list[str] = Field(default_factory=list)
    inventory_add: list[str] = Field(default_factory=list)
    inventory_remove: list[str] = Field(default_factory=list)
    journal_add: list[str] = Field(default_factory=list)
    facts_learned: list[str] = Field(default_factory=list)
    available_exits: list[str] = Field(default_factory=list)
    discovered_locations: list[str] = Field(default_factory=list)
    relationship_changes: list[RelationshipDelta] = Field(default_factory=list)
    consequence: Optional[str] = None
    danger_level: str = "calm"
    should_end_scene: bool = False


STATE_DELTA_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "location",
        "time_marker",
        "npcs_present",
        "companions_present",
        "inventory_add",
        "inventory_remove",
        "journal_add",
        "facts_learned",
        "available_exits",
        "discovered_locations",
        "relationship_changes",
        "consequence",
        "danger_level",
        "should_end_scene",
    ],
    "properties": {
        "location": {"type": ["string", "null"]},
        "time_marker": {"type": ["string", "null"]},
        "npcs_present": {"type": "array", "items": {"type": "string"}},
        "companions_present": {"type": "array", "items": {"type": "string"}},
        "inventory_add": {"type": "array", "items": {"type": "string"}},
        "inventory_remove": {"type": "array", "items": {"type": "string"}},
        "journal_add": {"type": "array", "items": {"type": "string"}},
        "facts_learned": {"type": "array", "items": {"type": "string"}},
        "available_exits": {"type": "array", "items": {"type": "string"}},
        "discovered_locations": {"type": "array", "items": {"type": "string"}},
        "relationship_changes": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["npc_name", "delta"],
                "properties": {
                    "npc_name": {"type": "string"},
                    "delta": {"type": "integer"},
                },
            },
        },
        "consequence": {"type": ["string", "null"]},
        "danger_level": {"type": "string", "enum": ["calm", "wary", "perilous"]},
        "should_end_scene": {"type": "boolean"},
    },
}
