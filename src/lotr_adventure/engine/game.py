from __future__ import annotations

from pathlib import Path

from rich.prompt import IntPrompt, Prompt

from lotr_adventure.ai.client import OpenAIClient
from lotr_adventure.ai.narrator import NarratorEngine
from lotr_adventure.ai.npc_chat import NpcChatEngine
from lotr_adventure.ai.state_updates import StateUpdateEngine
from lotr_adventure.config import Config
from lotr_adventure.domain.lore import LoreCatalog
from lotr_adventure.domain.models import GameState, LocationProfile, ParsedCommand, PlayableCharacter, StoryAnchor
from lotr_adventure.engine.commands import parse_command
from lotr_adventure.engine.saves import load_state, save_state
from lotr_adventure.ui.input import CommandInput
from lotr_adventure.ui.render import Renderer


class GameApp:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.lore = LoreCatalog.load()
        self.renderer = Renderer(config)
        self.client = OpenAIClient(config)
        self.narrator = NarratorEngine(self.client)
        self.npc_chat = NpcChatEngine(self.client)
        self.state_updates = StateUpdateEngine(self.client)
        self.state: GameState | None = None
        self.command_input = CommandInput(self._completion_words)

    def run(self) -> None:
        try:
            self.renderer.title("The Red Book Adventure")
            self.renderer.meta("Canon-leaning exploration across The Hobbit and The Lord of the Rings.")
            if not self.client.enabled:
                self.renderer.error("OPENAI_API_KEY is not set. The game will fall back to a minimal local narrator.")

            while True:
                options = self._startup_options()
                prompt = "  ".join(f"{idx + 1}) {label}" for idx, (label, _) in enumerate(options))
                choice = IntPrompt.ask(prompt, default=1)
                action = options[max(0, min(choice - 1, len(options) - 1))][1]
                if action == "new":
                    self.state = self._start_new_game()
                    break
                if action in {"resume", "load"}:
                    path = self._resolve_load_path(prefer=action)
                    if path is None:
                        self.renderer.error("No saved tale is available yet.")
                        continue
                    self.state = load_state(path)
                    self.renderer.system(f"Loaded {path.name}.")
                    break
                if action == "quit":
                    return

            assert self.state is not None
            self.renderer.show_state(self.state)
            self._show_onboarding()
            while True:
                raw = self.command_input.prompt(f"{self.state.location}> ").strip()
                command = parse_command(raw)
                if command.kind == "empty":
                    continue
                if not self.handle_command(command):
                    return
        except KeyboardInterrupt:
            self._graceful_exit_on_interrupt()
            return
        except EOFError:
            self._graceful_exit_on_interrupt()
            return

    def _graceful_exit_on_interrupt(self) -> None:
        if self.state is not None:
            save_state(self.config.autosave_file, self.state)
            self.renderer.system(f"Your road is preserved in {self.config.autosave_file.name}.")
        self.renderer.system("The tale is set aside.")

    def handle_command(self, command: ParsedCommand) -> bool:
        assert self.state is not None
        state = self.state

        if command.kind == "quit":
            self.renderer.system("The present tale is laid aside.")
            return False
        if command.kind == "help":
            self._show_help()
            return True
        if command.kind == "inventory":
            self.renderer.system(f"Inventory: {', '.join(state.inventory) or 'None'}")
            return True
        if command.kind == "journal":
            lines = state.journal or ["No journal entries yet."]
            self.renderer.show_options("Journal", lines)
            return True
        if command.kind == "objective":
            lines = [state.current_objective or "No active objective."]
            if state.current_guidance:
                lines.append(f"Guidance: {state.current_guidance}")
            if state.suggested_actions:
                lines.append(f"Suggested: {', '.join(state.suggested_actions)}")
            self.renderer.show_options("Current Objective", lines)
            return True
        if command.kind == "hint":
            self._show_hint()
            return True
        if command.kind == "story_status":
            self._show_story_status()
            return True
        if command.kind == "continue_story":
            self._continue_story()
            return True
        if command.kind == "party":
            self.renderer.system(f"Companions: {', '.join(state.companions) or 'None'}")
            return True
        if command.kind == "where":
            self.renderer.system(f"{state.book} | {state.chapter} | {state.location} | {state.time_marker}")
            return True
        if command.kind == "map":
            known = [f"Current: {state.location}"]
            known.extend(f"Road to {name}" for name in (state.available_exits or []))
            if state.visited_locations:
                known.append(f"Visited: {', '.join(state.visited_locations[-8:])}")
            self.renderer.show_options("Known Paths", known)
            return True
        if command.kind == "save":
            save_state(self.config.save_file, state)
            self.renderer.system(f"Saved to {self.config.save_file.name}.")
            return True
        if command.kind == "load":
            path = self._resolve_load_path(prefer="load")
            if path is None:
                self.renderer.error("No save file found.")
                return True
            self.state = load_state(path)
            self.renderer.system(f"Loaded {path.name}.")
            self.renderer.show_state(self.state)
            return True
        if command.kind in {"jump", "jump_menu"}:
            anchor = self._select_anchor(query=command.target) if command.kind == "jump" else self._select_anchor()
            if anchor is None:
                self.renderer.error("No matching anchor found.")
                return True
            if state.game_mode == "story" and anchor.id not in state.unlocked_anchors:
                self.renderer.error("That chapter is not yet open in Story Mode.")
                return True
            self._apply_anchor(anchor, reset_journal=False)
            return True
        if command.kind == "talk":
            if not command.target:
                self.renderer.error("Use 'talk <character>'.")
                return True
            npc_name = self._resolve_present_npc_name(command.target)
            if npc_name is None:
                self.renderer.error(f"{command.target} is not presently before you.")
                return True
            self._conversation_loop(npc_name)
            return True
        if command.kind == "ask":
            if not command.target or not command.topic:
                self.renderer.error("Use 'ask <character> about <topic>'.")
                return True
            npc_name = self._resolve_present_npc_name(command.target)
            if npc_name is None:
                self.renderer.error(f"{command.target} is not presently before you.")
                return True
            line = f"What can you tell me about {command.topic}?"
            reply = self.npc_chat.reply(
                state,
                npc_name,
                line,
                self.lore.get_npc(npc_name),
                self.lore.get_location(state.location),
            )
            self._record_npc_interaction(npc_name)
            self.renderer.npc(npc_name, reply)
            return True

        self._run_scene_command(command)
        return True

    def _start_new_game(self) -> GameState:
        mode = self._select_mode()
        character = self._select_character()
        if mode == "story":
            path = self._select_story_path(character)
            first_step = path.steps[0]
            return self._apply_anchor(
                self.lore.get_anchor(first_step.anchor_id),
                character_override=character,
                reset_journal=True,
                mode=mode,
                story_path_id=path.id,
                story_step_index=0,
                unlocked_anchors=[first_step.anchor_id],
                current_objective=first_step.objective,
                current_guidance=first_step.guidance,
                suggested_actions=first_step.suggested_actions,
                completed_objectives=[],
            )
        anchor = self._select_anchor_for_character(character)
        return self._apply_anchor(anchor, character_override=character, reset_journal=True, mode=mode)

    def _select_mode(self) -> str:
        self.renderer.show_options(
            "Choose A Mode",
            [
                "1) Story Mode - guided chapter progression with canon pressure",
                "2) Open Mode - freely jump among your character's anchors",
            ],
        )
        selected = IntPrompt.ask("Select a mode", default=1)
        return "story" if selected == 1 else "open"

    def _startup_options(self) -> list[tuple[str, str]]:
        options: list[tuple[str, str]] = [("New game", "new")]
        if self.config.autosave_file.exists():
            options.append(("Resume autosave", "resume"))
        if self.config.save_file.exists():
            options.append(("Load savegame", "load"))
        options.append(("Quit", "quit"))
        return options

    def _resolve_load_path(self, *, prefer: str) -> Path | None:
        if prefer == "resume":
            candidates = [self.config.autosave_file, self.config.save_file]
        else:
            candidates = [self.config.save_file, self.config.autosave_file]
        for path in candidates:
            if path.exists():
                return path
        return None

    def _select_character(self) -> PlayableCharacter:
        characters = self.lore.list_characters()
        options = [f"{idx + 1}) {char.display_name} - {char.summary}" for idx, char in enumerate(characters)]
        self.renderer.show_options("Choose Your Character", options)
        selected = IntPrompt.ask("Select a character", default=1)
        return characters[max(0, min(selected - 1, len(characters) - 1))]

    def _select_anchor_for_character(self, character: PlayableCharacter) -> StoryAnchor:
        anchors = [anchor for anchor in self.lore.list_anchors() if anchor.viewpoint_character_id == character.id]
        options = [f"{idx + 1}) {anchor.label} - {anchor.book}, {anchor.chapter}" for idx, anchor in enumerate(anchors)]
        self.renderer.show_options("Choose A Story Anchor", options)
        selected = IntPrompt.ask("Select an anchor", default=1)
        return anchors[max(0, min(selected - 1, len(anchors) - 1))]

    def _select_story_path(self, character: PlayableCharacter):
        paths = self.lore.list_story_paths_for_character(character.id)
        options = [f"{idx + 1}) {path.label} - {path.summary}" for idx, path in enumerate(paths)]
        self.renderer.show_options("Choose A Story Path", options)
        selected = IntPrompt.ask("Select a path", default=1)
        return paths[max(0, min(selected - 1, len(paths) - 1))]

    def _select_anchor(self, query: str | None = None) -> StoryAnchor | None:
        state = self.state
        if query:
            anchor = self.lore.find_anchor(query)
            if state is not None and state.game_mode == "story" and anchor is not None and anchor.id not in state.unlocked_anchors:
                return None
            return anchor
        anchors = self.lore.list_anchors()
        if state is not None and state.game_mode == "story":
            anchors = [anchor for anchor in anchors if anchor.id in state.unlocked_anchors]
        options = [f"{idx + 1}) {anchor.id} - {anchor.label}" for idx, anchor in enumerate(anchors)]
        self.renderer.show_options("Jump To Anchor", options)
        selected = IntPrompt.ask("Select an anchor", default=1)
        return anchors[max(0, min(selected - 1, len(anchors) - 1))]

    def _apply_anchor(
        self,
        anchor: StoryAnchor,
        *,
        character_override: PlayableCharacter | None = None,
        reset_journal: bool = False,
        mode: str | None = None,
        story_path_id: str | None = None,
        story_step_index: int | None = None,
        unlocked_anchors: list[str] | None = None,
        current_objective: str | None = None,
        current_guidance: str | None = None,
        suggested_actions: list[str] | None = None,
        completed_objectives: list[str] | None = None,
    ) -> GameState:
        character = character_override or self.lore.get_character(anchor.viewpoint_character_id)
        prior_journal = [] if reset_journal or self.state is None else self.state.journal[:]
        prior_journal.append(f"Entered anchor: {anchor.label}.")
        previous = self.state
        state = GameState(
            player_character_id=character.id,
            player_name=character.display_name,
            game_mode=mode or (previous.game_mode if previous is not None else "open"),
            anchor_id=anchor.id,
            book=anchor.book,
            chapter=anchor.chapter,
            location=anchor.location,
            time_marker=anchor.time_marker,
            story_path_id=story_path_id if story_path_id is not None else (previous.story_path_id if previous is not None else ""),
            story_step_index=story_step_index if story_step_index is not None else (previous.story_step_index if previous is not None else 0),
            unlocked_anchors=unlocked_anchors[:] if unlocked_anchors is not None else (previous.unlocked_anchors[:] if previous is not None else []),
            current_objective=current_objective if current_objective is not None else (previous.current_objective if previous is not None else ""),
            current_guidance=current_guidance if current_guidance is not None else (previous.current_guidance if previous is not None else ""),
            suggested_actions=suggested_actions[:] if suggested_actions is not None else (previous.suggested_actions[:] if previous is not None else []),
            completed_objectives=completed_objectives[:] if completed_objectives is not None else (previous.completed_objectives[:] if previous is not None else []),
            inventory=(character.starting_inventory[:] if reset_journal or previous is None else previous.inventory[:]),
            companions=(
                anchor.starting_companions[:]
                if reset_journal or previous is None
                else list(dict.fromkeys(previous.companions[:] + anchor.starting_companions[:]))
            ),
            npcs_present=anchor.starting_npcs[:],
            available_exits=anchor.available_exits[:],
            visited_locations=([anchor.location] if reset_journal or previous is None else previous.visited_locations[:] + [anchor.location]),
            location_history=([anchor.location] if reset_journal or previous is None else previous.location_history[:] + [anchor.location]),
            spoken_to_npcs=[] if reset_journal or previous is None else previous.spoken_to_npcs[:],
            inspected_targets=[] if reset_journal or previous is None else previous.inspected_targets[:],
            journal=prior_journal,
            facts=([anchor.summary] if reset_journal or previous is None else previous.facts[:] + [anchor.summary]),
            narrator_history=[],
            npc_threads={} if reset_journal or previous is None else previous.npc_threads.copy(),
            npc_memories={} if reset_journal or previous is None else previous.npc_memories.copy(),
            npc_relationships={} if reset_journal or previous is None else previous.npc_relationships.copy(),
        )
        location = self.lore.get_location(anchor.location)
        if location is not None:
            state.available_exits = location.linked_locations[:]
            state.npcs_present = list(dict.fromkeys(anchor.starting_npcs + state.companions))
        state.visited_locations = list(dict.fromkeys(state.visited_locations))
        opening = self.narrator.opening_scene(state, character, anchor, location)
        state.last_narration = opening
        state.narrator_history = [
            {"role": "user", "content": f"Open at anchor {anchor.label}."},
            {"role": "assistant", "content": opening},
        ]
        self.state = state
        if location is not None:
            self._learn_location_fact(location)
        self.renderer.chapter_card(state, character, anchor)
        self.renderer.narrate(opening)
        self.renderer.show_state(state)
        save_state(self.config.autosave_file, state)
        return state

    def _run_scene_command(self, command: ParsedCommand) -> None:
        assert self.state is not None
        state = self.state
        anchor = self.lore.get_anchor(state.anchor_id)
        character = self.lore.get_character(state.player_character_id)
        location = self.lore.get_location(state.location)
        command_for_narrator = self._prepare_command_text(command, location)
        narration = self.narrator.narrate_action(state, character, anchor, command_for_narrator, location)
        state.narrator_history.append({"role": "user", "content": command.raw})
        state.narrator_history.append({"role": "assistant", "content": narration})
        state.narrator_history = state.narrator_history[-12:]
        self.renderer.narrate(narration)
        self._apply_local_effects(command, location)
        delta = self.state_updates.generate(state, command.raw, narration, self.lore.get_location(state.location))
        self._apply_state_delta(delta)
        state.last_narration = narration
        save_state(self.config.autosave_file, state)
        self.renderer.show_state(state)

    def _apply_local_effects(self, command: ParsedCommand, location: LocationProfile | None) -> None:
        assert self.state is not None
        if command.kind == "travel" and command.target:
            resolved = self._resolve_travel_target(command.target, location)
            if resolved is not None:
                self.state.location = resolved.name
                self.state.available_exits = resolved.linked_locations[:]
                self.state.npcs_present = list(dict.fromkeys(self.state.npcs_present + self.state.companions))
                self.state.visited_locations.append(resolved.name)
                self.state.visited_locations = list(dict.fromkeys(self.state.visited_locations))
                self.state.location_history.append(resolved.name)
                self.state.journal.append(f"Travelled to {resolved.name}.")
                self._learn_location_fact(resolved)
            else:
                self.state.journal.append(f"Sought a road toward {command.target}.")
        elif command.kind == "inspect" and command.target:
            self.state.journal.append(f"Inspected {command.target}.")
            self.state.inspected_targets.append(command.target)
            self.state.inspected_targets = list(dict.fromkeys(self.state.inspected_targets))
            if location is not None:
                for landmark in location.landmarks:
                    if command.target.lower() in landmark.lower():
                        self.state.facts.append(f"{location.name}: {landmark}")
                        break
        elif command.kind == "look":
            self.state.journal.append(f"Looked about at {self.state.location}.")
            if location is not None:
                observation = f"{location.name}: {location.summary}"
                if observation not in self.state.facts:
                    self.state.facts.append(observation)
                if location.atmosphere:
                    mood = f"{location.name} feels {', '.join(location.atmosphere[:2])}."
                    if mood not in self.state.facts:
                        self.state.facts.append(mood)
        elif command.kind == "unknown":
            self.state.journal.append(f"Tried: {command.raw}")

    def _apply_state_delta(self, delta) -> None:
        assert self.state is not None
        state = self.state
        if delta.location:
            state.location = delta.location
        if delta.time_marker:
            state.time_marker = delta.time_marker
        if delta.npcs_present:
            state.npcs_present = delta.npcs_present
        if delta.companions_present:
            state.companions = delta.companions_present
        if delta.available_exits:
            state.available_exits = delta.available_exits
        for name in delta.discovered_locations:
            if name not in state.visited_locations:
                state.visited_locations.append(name)
        for item in delta.inventory_add:
            if item not in state.inventory:
                state.inventory.append(item)
        for item in delta.inventory_remove:
            if item in state.inventory:
                state.inventory.remove(item)
        for entry in delta.journal_add:
            state.journal.append(entry)
        for fact in delta.facts_learned:
            if fact not in state.facts:
                state.facts.append(fact)
        for change in delta.relationship_changes:
            state.npc_relationships[change.npc_name] = (
                state.npc_relationships.get(change.npc_name, 0) + change.delta
            )
        if delta.consequence:
            state.journal.append(delta.consequence)

    def _conversation_loop(self, npc_name: str) -> None:
        assert self.state is not None
        self.renderer.system(f"You begin speaking with {npc_name}. Type 'bye' to return.")
        while True:
            line = Prompt.ask("You")
            if line.strip().lower() in {"bye", "goodbye", "exit"}:
                self.renderer.system("You return to the road of the larger tale.")
                return
            reply = self.npc_chat.reply(
                self.state,
                npc_name,
                line,
                self.lore.get_npc(npc_name),
                self.lore.get_location(self.state.location),
            )
            self._record_npc_interaction(npc_name)
            self.renderer.npc(npc_name, reply)

    def _completion_words(self) -> list[str]:
        if self.state is None:
            return ["look", "save", "load", "quit"]
        location = self.lore.get_location(self.state.location)
        return sorted(
            {
                "look",
                "objective",
                "story",
                "continue",
                "inventory",
                "journal",
                "party",
                "where",
                "map",
                "save",
                "load",
                "help",
                "quit",
                "jump",
                *self.state.suggested_actions,
                *(f"go {exit_name}" for exit_name in self.state.available_exits),
                *(f"talk {npc}" for npc in self.state.npcs_present),
                *(f"inspect {landmark}" for landmark in (location.landmarks if location is not None else [])),
                *self.state.available_exits,
                *self.state.npcs_present,
            }
        )

    def _resolve_present_npc_name(self, query: str) -> str | None:
        assert self.state is not None
        needle = query.strip().lower()
        for npc_name in self.state.npcs_present:
            if needle == npc_name.lower() or needle in npc_name.lower():
                return npc_name
        return None

    def _prepare_command_text(self, command: ParsedCommand, location: LocationProfile | None) -> str:
        if command.kind != "travel" or not command.target:
            return command.raw
        resolved = self._resolve_travel_target(command.target, location)
        if resolved is None:
            return (
                f"attempt to travel toward {command.target}, though no known road or path from "
                f"{self.state.location if self.state else 'here'} leads there"
            )
        return f"travel to {resolved.name}"

    def _resolve_travel_target(self, target: str, current_location: LocationProfile | None) -> LocationProfile | None:
        if current_location is None:
            return None
        for linked_name in current_location.linked_locations:
            linked = self.lore.get_location(linked_name)
            if linked and self.lore._matches_location(linked, target.strip().lower()):
                return linked
        return None

    def _learn_location_fact(self, location: LocationProfile) -> None:
        assert self.state is not None
        fact = f"{location.name} in {location.region}: {location.summary}"
        if fact not in self.state.facts:
            self.state.facts.append(fact)

    def _show_help(self) -> None:
        assert self.state is not None
        lines = [
            "look",
            "go <place>",
            "inspect <thing>",
            "talk <character>",
            "ask <character> about <topic>",
            "hint",
            "jump <anchor>",
            "where",
            "map",
            "objective",
            "story",
            "continue",
            "inventory",
            "journal",
            "party",
            "save",
            "load",
            "quit",
            "Manual save writes savegame.json; scene changes also refresh autosave.json.",
        ]
        if self.state.game_mode == "story":
            lines.append("Story Mode: use 'objective', 'hint', and 'continue'; 'jump' only reaches chapters already opened.")
            lines.append("Story Mode: 'continue' advances only when the current chapter's work is truly done.")
        else:
            lines.append("Open Mode: use 'jump' freely among the current viewpoint's anchors to roam the wider tale.")
        self.renderer.show_options("Commands", lines)

    def _show_onboarding(self) -> None:
        assert self.state is not None
        lines = [
            f"You stand in {self.state.location}.",
            "Use 'look' to gather the scene, 'talk <character>' to open conversation, and 'go <place>' to travel locally.",
            "Use 'hint' if you want quiet guidance without breaking the fiction.",
            "Use 'save' for a deliberate milestone; the game also keeps an autosave after scene changes.",
        ]
        if self.state.game_mode == "story":
            lines.append("Story Mode: follow 'objective' and 'continue' to move chapter by chapter; 'jump' is limited to opened chapters.")
        else:
            lines.append("Open Mode: use 'jump' to move broadly across your viewpoint character's anchor scenes.")
        if self.state.current_objective:
            lines.append(f"Your present charge: {self.state.current_objective}")
        self.renderer.show_options("How To Begin", lines)

    def _show_hint(self) -> None:
        assert self.state is not None
        lines: list[str] = []
        if self.state.current_guidance:
            lines.append(self.state.current_guidance)
        if self.state.suggested_actions:
            lines.append(f"The tale presently leans toward: {', '.join(self.state.suggested_actions[:4])}")
        elif self.state.npcs_present:
            lines.append(f"Someone near at hand may be worth addressing: {self.state.npcs_present[0]}.")
        elif self.state.available_exits:
            lines.append(f"A road lies open toward {self.state.available_exits[0]}.")
        else:
            lines.append("Pause, look closely, and attend to the temper of the place before acting.")
        if self.state.game_mode == "story":
            path = self.lore.get_story_path(self.state.story_path_id) if self.state.story_path_id else None
            if path is not None:
                missing = self._missing_story_requirements(path.steps[self.state.story_step_index])
                if missing:
                    lines.append(f"What remains in this chapter: {'; '.join(missing[:3])}")
        self.renderer.show_options("Quiet Guidance", lines)

    def _show_story_status(self) -> None:
        assert self.state is not None
        if self.state.game_mode != "story" or not self.state.story_path_id:
            self.renderer.system("You are in Open Mode. No guided story path is active.")
            return
        path = self.lore.get_story_path(self.state.story_path_id)
        lines = [
            f"Path: {path.label}",
            f"Current objective: {self.state.current_objective or 'None'}",
            f"Unlocked chapters: {', '.join(self.state.unlocked_anchors)}",
        ]
        if self.state.current_guidance:
            lines.append(f"Guidance: {self.state.current_guidance}")
        if self.state.suggested_actions:
            lines.append(f"Suggested: {', '.join(self.state.suggested_actions)}")
        missing = self._missing_story_requirements(path.steps[self.state.story_step_index])
        if missing:
            lines.append(f"Still needed: {'; '.join(missing)}")
        if self.state.completed_objectives:
            lines.append(f"Completed: {', '.join(self.state.completed_objectives[-3:])}")
        self.renderer.show_options("Story Status", lines)

    def _continue_story(self) -> None:
        assert self.state is not None
        state = self.state
        if state.game_mode != "story" or not state.story_path_id:
            self.renderer.system("There is no guided story path to continue.")
            return
        path = self.lore.get_story_path(state.story_path_id)
        current_step = path.steps[state.story_step_index]
        missing = self._missing_story_requirements(current_step)
        if missing:
            self.renderer.show_options(
                "Story Not Yet Ready",
                ["You have not yet fulfilled this chapter's work."] + missing,
            )
            return
        if current_step.title not in state.completed_objectives:
            state.completed_objectives.append(current_step.title)
        state.journal.append(f"Completed story chapter: {current_step.title}.")
        next_index = state.story_step_index + 1
        if next_index >= len(path.steps):
            self.renderer.system("This story path has reached its present end.")
            return
        next_step = path.steps[next_index]
        unlocked = state.unlocked_anchors[:]
        if next_step.anchor_id not in unlocked:
            unlocked.append(next_step.anchor_id)
        self._apply_anchor(
            self.lore.get_anchor(next_step.anchor_id),
            mode="story",
            story_path_id=path.id,
            story_step_index=next_index,
            unlocked_anchors=unlocked,
            current_objective=next_step.objective,
            current_guidance=next_step.guidance,
            suggested_actions=next_step.suggested_actions,
            completed_objectives=state.completed_objectives,
        )

    def _record_npc_interaction(self, npc_name: str) -> None:
        assert self.state is not None
        self.state.spoken_to_npcs.append(npc_name)
        self.state.spoken_to_npcs = list(dict.fromkeys(self.state.spoken_to_npcs))
        journal_line = f"Spoke with {npc_name}."
        if journal_line not in self.state.journal:
            self.state.journal.append(journal_line)
        npc = self.lore.get_npc(npc_name)
        if npc is not None:
            fact = f"{npc_name} of {npc.affiliation}: {npc.summary}"
            if fact not in self.state.facts:
                self.state.facts.append(fact)

    def _missing_story_requirements(self, step) -> list[str]:
        assert self.state is not None
        missing: list[str] = []
        for location in step.required_locations:
            if location not in self.state.visited_locations:
                missing.append(f"Travel to {location}.")
        for npc_name in step.required_npcs:
            if npc_name not in self.state.spoken_to_npcs:
                missing.append(f"Speak with {npc_name}.")
        for target in step.required_inspections:
            if target not in self.state.inspected_targets:
                missing.append(f"Inspect {target}.")
        facts_joined = " ".join(self.state.facts).lower()
        for keyword in step.required_fact_keywords:
            if keyword.lower() not in facts_joined:
                missing.append(f"Learn more related to '{keyword}'.")
        return missing
