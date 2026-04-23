import unittest

from lotr_adventure.ai.prompts import narrator_instructions, npc_instructions
from lotr_adventure.domain.lore import LoreCatalog
from lotr_adventure.domain.models import GameState


class PromptContractTests(unittest.TestCase):
    def test_narrator_instructions_keep_world_boundary_and_scene_beats(self):
        lore = LoreCatalog.load()
        character = lore.get_character("bilbo")
        anchor = lore.get_anchor("bilbo_in_smaugs_lair")

        instructions = narrator_instructions(character, anchor)

        self.assertIn("Never mention the real world", instructions)
        self.assertIn("book canon", instructions)
        self.assertIn("scene beats", instructions)
        self.assertIn("Smaug", instructions)

    def test_npc_instructions_include_inner_life_and_relationship_context(self):
        lore = LoreCatalog.load()
        state = GameState(
            player_character_id="gandalf",
            player_name="Gandalf, the Grey Pilgrim",
            game_mode="story",
            anchor_id="gandalf_in_meduseld",
            book="The Two Towers",
            chapter="The King of the Golden Hall",
            location="Meduseld",
            time_marker="A clear hard day in the Riddermark",
            npc_relationships={"Théoden": 2},
        )

        instructions = npc_instructions(
            state,
            "Théoden",
            lore.get_npc("Théoden"),
            lore.get_location("Meduseld"),
            ["Player raised: Wormtongue's counsel."],
        )

        self.assertIn("Remain entirely in character", instructions)
        self.assertIn("Only know what someone in your station, place, and time could plausibly know.", instructions)
        self.assertIn("inner life", instructions)
        self.assertIn("your current stance toward them", instructions)
        self.assertIn("Riddermark", instructions)

    def test_npc_instructions_for_galadriel_include_lorien_context(self):
        lore = LoreCatalog.load()
        state = GameState(
            player_character_id="frodo",
            player_name="Frodo Baggins, Ring-bearer of the Shire",
            game_mode="story",
            anchor_id="frodo_in_lorien",
            book="The Fellowship of the Ring",
            chapter="Lothlórien",
            location="Lothlórien",
            time_marker="A clear golden morning among the mallorn trees",
        )

        instructions = npc_instructions(
            state,
            "Galadriel",
            lore.get_npc("Galadriel"),
            lore.get_location("Lothlórien"),
            [],
        )

        self.assertIn("Golden Wood", instructions)
        self.assertIn("the hearts of those who stand before her", instructions)
        self.assertIn("Remain entirely in character", instructions)
