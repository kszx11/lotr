import unittest
from pathlib import Path

from lotr_adventure.domain.models import GameState
from lotr_adventure.engine.saves import load_state, save_state


class SaveTests(unittest.TestCase):
    def test_save_round_trip(self):
        import tempfile

        state = GameState(
            player_character_id="frodo",
            player_name="Frodo Baggins, Ring-bearer of the Shire",
            game_mode="story",
            anchor_id="frodo_departs_shire",
            book="The Fellowship of the Ring",
            chapter="Three Is Company",
            location="The Shire",
            time_marker="Early autumn evening",
            story_path_id="frodo_ring_bearer",
            story_step_index=0,
            unlocked_anchors=["frodo_departs_shire"],
            current_objective="Set out from home.",
            current_guidance="Keep the Shire vivid enough that its loss matters.",
            suggested_actions=["talk Sam", "talk Pippin", "go Woody End"],
            completed_objectives=[],
            inventory=["elven cloak"],
            companions=["Samwise Gamgee"],
            npcs_present=["Samwise Gamgee"],
            available_exits=["Woody End"],
            visited_locations=["The Shire"],
            location_history=["The Shire"],
            spoken_to_npcs=["Samwise Gamgee"],
            inspected_targets=["lane"],
            journal=["Set out from home."],
            facts=["The road east waits."],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "savegame.json"
            save_state(path, state)
            loaded = load_state(path)

        self.assertEqual(loaded.location, state.location)
        self.assertEqual(loaded.inventory, state.inventory)
        self.assertEqual(loaded.journal, state.journal)
        self.assertEqual(loaded.visited_locations, state.visited_locations)
        self.assertEqual(loaded.current_guidance, state.current_guidance)
        self.assertEqual(loaded.suggested_actions, state.suggested_actions)
        self.assertEqual(loaded.spoken_to_npcs, state.spoken_to_npcs)
