from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from lotr_adventure.domain.models import (
    LocationProfile,
    NpcProfile,
    PlayableCharacter,
    StoryAnchor,
    StoryPath,
    StoryStep,
)


@dataclass
class LoreCatalog:
    characters: dict[str, PlayableCharacter]
    anchors: dict[str, StoryAnchor]
    npcs: dict[str, NpcProfile]
    locations: dict[str, LocationProfile]
    story_paths: dict[str, StoryPath]

    @classmethod
    def load(cls) -> "LoreCatalog":
        base = Path(__file__).resolve().parents[1] / "content"
        characters_raw = yaml.safe_load((base / "playable_characters.yaml").read_text())
        anchors_raw = yaml.safe_load((base / "story_anchors.yaml").read_text())
        npcs_raw = yaml.safe_load((base / "npc_profiles.yaml").read_text())
        locations_raw = yaml.safe_load((base / "locations.yaml").read_text())
        paths_raw = yaml.safe_load((base / "story_paths.yaml").read_text())
        characters = {item["id"]: PlayableCharacter(**item) for item in characters_raw["characters"]}
        anchors = {item["id"]: StoryAnchor(**item) for item in anchors_raw["anchors"]}
        npcs = {item["name"]: NpcProfile(**item) for item in npcs_raw["npcs"]}
        locations = {item["name"]: LocationProfile(**item) for item in locations_raw["locations"]}
        story_paths = {
            item["id"]: StoryPath(
                id=item["id"],
                label=item["label"],
                character_id=item["character_id"],
                summary=item["summary"],
                steps=[StoryStep(**step) for step in item["steps"]],
            )
            for item in paths_raw["story_paths"]
        }
        return cls(characters=characters, anchors=anchors, npcs=npcs, locations=locations, story_paths=story_paths)

    def list_characters(self) -> list[PlayableCharacter]:
        return list(self.characters.values())

    def list_anchors(self) -> list[StoryAnchor]:
        return list(self.anchors.values())

    def get_character(self, character_id: str) -> PlayableCharacter:
        return self.characters[character_id]

    def get_anchor(self, anchor_id: str) -> StoryAnchor:
        return self.anchors[anchor_id]

    def get_story_path(self, path_id: str) -> StoryPath:
        return self.story_paths[path_id]

    def list_story_paths_for_character(self, character_id: str) -> list[StoryPath]:
        return [path for path in self.story_paths.values() if path.character_id == character_id]

    def get_npc(self, npc_name: str) -> NpcProfile | None:
        return self.npcs.get(npc_name)

    def get_location(self, location_name: str) -> LocationProfile | None:
        return self.locations.get(location_name)

    def find_location(self, query: str, from_location: str | None = None) -> LocationProfile | None:
        needle = query.strip().lower()
        if not needle:
            return None
        current = self.locations.get(from_location) if from_location else None
        if current:
            for linked_name in current.linked_locations:
                profile = self.locations.get(linked_name)
                if profile and self._matches_location(profile, needle):
                    return profile
            return None
        for profile in self.locations.values():
            if self._matches_location(profile, needle):
                return profile
        return None

    def find_anchor(self, query: str) -> StoryAnchor | None:
        needle = query.strip().lower()
        if not needle:
            return None
        if needle in self.anchors:
            return self.anchors[needle]
        for anchor in self.anchors.values():
            haystacks = (anchor.id, anchor.label, anchor.location, anchor.chapter, anchor.book)
            if any(needle in value.lower() for value in haystacks):
                return anchor
        return None

    @staticmethod
    def _matches_location(profile: LocationProfile, needle: str) -> bool:
        haystacks = [profile.id, profile.name, profile.region, *profile.travel_keywords, *profile.landmarks]
        return any(needle in value.lower() for value in haystacks)
