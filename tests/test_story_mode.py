import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lotr_adventure.config import Config
from lotr_adventure.domain.models import GameState, ParsedCommand
from lotr_adventure.engine.game import GameApp
from lotr_adventure.engine.saves import save_state


class _SilentRenderer:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.option_panels: list[tuple[str, list[str]]] = []
        self.state_panels = 0
        self.narrations: list[str] = []

    def title(self, text: str) -> None:
        return

    def meta(self, text: str) -> None:
        return

    def error(self, text: str) -> None:
        return

    def show_state(self, state) -> None:
        self.state_panels += 1
        return

    def system(self, text: str) -> None:
        self.messages.append(text)
        return

    def show_options(self, title: str, options: list[str]) -> None:
        self.option_panels.append((title, options))
        return

    def chapter_card(self, state, character, anchor) -> None:
        return

    def narrate(self, text: str) -> None:
        self.narrations.append(text)
        return

    def npc(self, npc_name: str, text: str) -> None:
        return


class StoryModeTests(unittest.TestCase):
    def _make_app(self) -> GameApp:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config = Config(
            api_key=None,
            text_model="gpt-4.1-mini",
            structured_model="gpt-4o-mini",
            typewriter_delay=0,
            reduced_motion=True,
            root_dir=Path(temp_dir.name),
        )
        app = GameApp(config)
        app.renderer = _SilentRenderer()
        return app

    def _sample_state(self) -> GameState:
        return GameState(
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

    def test_startup_options_include_resume_when_autosave_exists(self):
        app = self._make_app()
        save_state(app.config.autosave_file, self._sample_state())
        self.assertEqual(
            app._startup_options(),
            [("New game", "new"), ("Resume autosave", "resume"), ("Quit", "quit")],
        )

    def test_resume_replays_scene_narration(self):
        app = self._make_app()
        state = self._sample_state()
        state.last_narration = "The Shire lies quiet before the road."
        save_state(app.config.autosave_file, state)
        app.command_input.prompt = lambda _: "quit"
        with patch("lotr_adventure.engine.game.IntPrompt.ask", side_effect=[2]):
            app.run()
        self.assertIn("The Shire lies quiet before the road.", app.renderer.narrations)

    def test_resolve_load_path_prefers_manual_save_for_load_and_autosave_for_resume(self):
        app = self._make_app()
        save_state(app.config.save_file, self._sample_state())
        save_state(app.config.autosave_file, self._sample_state())
        self.assertEqual(app._resolve_load_path(prefer="load"), app.config.save_file)
        self.assertEqual(app._resolve_load_path(prefer="resume"), app.config.autosave_file)

    def test_anchor_opening_uses_scene_starting_npcs_not_location_global_residents(self):
        app = self._make_app()
        bilbo = app.lore.get_character("bilbo")
        anchor = app.lore.get_anchor("unexpected_party")
        app._apply_anchor(anchor, character_override=bilbo, reset_journal=True, mode="story")
        self.assertEqual(app.state.npcs_present, ["Gandalf", "Thorin Oakenshield"])

    def test_new_game_renders_present_state_once(self):
        app = self._make_app()
        inputs = iter(["quit"])
        app.command_input.prompt = lambda _: next(inputs)
        with patch("lotr_adventure.engine.game.IntPrompt.ask", side_effect=[1, 1, 1, 1]):
            app.run()
        self.assertEqual(app.renderer.state_panels, 1)

    def test_keyboard_interrupt_during_main_prompt_exits_gracefully(self):
        app = self._make_app()
        app.command_input.prompt = lambda _: (_ for _ in ()).throw(KeyboardInterrupt())
        app.state = self._sample_state()
        app.run()
        self.assertIn("The tale is set aside.", app.renderer.messages)

    def test_keyboard_interrupt_during_npc_chat_exits_gracefully(self):
        app = self._make_app()
        inputs = iter(["talk Gandalf"])
        app.command_input.prompt = lambda _: next(inputs)
        with (
            patch("lotr_adventure.engine.game.IntPrompt.ask", side_effect=[1, 1, 1, 1]),
            patch("lotr_adventure.engine.game.Prompt.ask", side_effect=KeyboardInterrupt()),
        ):
            app.run()
        self.assertIn("Your road is preserved in autosave.json.", app.renderer.messages)
        self.assertIn("The tale is set aside.", app.renderer.messages)

    def test_open_mode_hint_offers_local_and_jump_suggestions(self):
        app = self._make_app()
        bilbo = app.lore.get_character("bilbo")
        anchor = app.lore.get_anchor("unexpected_party")
        app._apply_anchor(anchor, character_override=bilbo, reset_journal=True, mode="open")
        app._show_hint()
        title, options = app.renderer.option_panels[-1]
        self.assertEqual(title, "Quiet Guidance")
        self.assertTrue(any("talk Gandalf" in line for line in options))
        self.assertTrue(any("inspect round green door" in line for line in options))
        self.assertTrue(any("go The Green Dragon" in line for line in options))
        self.assertTrue(any("jump " in line for line in options))

    def test_story_continue_requires_scene_work_before_advancing(self):
        app = self._make_app()
        path = app.lore.get_story_path("frodo_ring_bearer")
        character = app.lore.get_character("frodo")
        first_step = path.steps[0]
        app._apply_anchor(
            app.lore.get_anchor(first_step.anchor_id),
            character_override=character,
            reset_journal=True,
            mode="story",
            story_path_id=path.id,
            story_step_index=0,
            unlocked_anchors=[first_step.anchor_id],
            current_objective=first_step.objective,
            current_guidance=first_step.guidance,
            suggested_actions=first_step.suggested_actions,
            completed_objectives=[],
        )

        app._continue_story()
        self.assertEqual(app.state.story_step_index, 0)

        app._record_npc_interaction("Samwise Gamgee")
        app._record_npc_interaction("Pippin Took")
        app._apply_local_effects(
            ParsedCommand(kind="travel", raw="go Woody End", target="Woody End"),
            app.lore.get_location("The Shire"),
        )
        app._apply_local_effects(
            ParsedCommand(kind="look", raw="look"),
            app.lore.get_location(app.state.location),
        )
        app._continue_story()

        self.assertEqual(app.state.story_step_index, 1)
        self.assertEqual(app.state.anchor_id, "frodo_in_old_forest")
        self.assertIn("frodo_in_old_forest", app.state.unlocked_anchors)

    def test_story_continue_blocks_until_required_inspection_is_done(self):
        app = self._make_app()
        path = app.lore.get_story_path("frodo_ring_bearer")
        character = app.lore.get_character("frodo")
        bree_index = 4
        second_step = path.steps[bree_index]
        app._apply_anchor(
            app.lore.get_anchor(second_step.anchor_id),
            character_override=character,
            reset_journal=True,
            mode="story",
            story_path_id=path.id,
            story_step_index=bree_index,
            unlocked_anchors=[step.anchor_id for step in path.steps[: bree_index + 1]],
            current_objective=second_step.objective,
            current_guidance=second_step.guidance,
            suggested_actions=second_step.suggested_actions,
            completed_objectives=[step.title for step in path.steps[:bree_index]],
        )

        app._record_npc_interaction("Aragorn")
        app._apply_local_effects(ParsedCommand(kind="look", raw="look"), app.lore.get_location(app.state.location))
        app._continue_story()
        self.assertEqual(app.state.anchor_id, "frodo_at_bree")

        app._apply_local_effects(
            ParsedCommand(kind="inspect", raw="inspect common room", target="common room"),
            app.lore.get_location(app.state.location),
        )
        app._continue_story()

        self.assertEqual(app.state.anchor_id, "frodo_at_weathertop")
