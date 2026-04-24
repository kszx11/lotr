import unittest

from lotr_adventure.ai.npc_chat import NpcChatEngine
from lotr_adventure.domain.lore import LoreCatalog
from lotr_adventure.domain.models import GameState


class NpcChatTests(unittest.TestCase):
    def test_guarded_reply_for_question_about_present_viewpoint_character(self):
        lore = LoreCatalog.load()
        engine = NpcChatEngine(client=type("Client", (), {})())
        state = GameState(
            player_character_id="treebeard",
            player_name="Treebeard, Ent of Fangorn",
            game_mode="story",
            anchor_id="treebeard_green_hollow",
            anchor_label="Treebeard in the Green Hollow",
            book="The Two Towers",
            chapter="Treebeard",
            location="The Green Hollow",
            time_marker="Morning under Fangorn's boughs",
            npcs_present=["Gandalf", "Treebeard"],
            available_exits=["Fangorn Forest", "Entmoot Dingle"],
        )

        reply = engine.reply(
            state,
            "Gandalf",
            "Where is Treebeard?",
            lore.get_npc("Gandalf"),
            lore.get_location("The Green Hollow"),
        )

        self.assertIn("stands before me now", reply)
        self.assertNotIn("you are treebeard", reply.lower())
