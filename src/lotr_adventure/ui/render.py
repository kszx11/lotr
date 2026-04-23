from __future__ import annotations

import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lotr_adventure.config import Config
from lotr_adventure.domain.models import GameState, PlayableCharacter, StoryAnchor
from lotr_adventure.ui import theme


class Renderer:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.console = Console()

    def title(self, text: str) -> None:
        self.console.print(Panel.fit(text, border_style=theme.TITLE, title="Middle-earth"))

    def narrate(self, text: str) -> None:
        self._stream(text, theme.NARRATION)

    def npc(self, npc_name: str, text: str) -> None:
        self.console.print(f"[{theme.NPC}]{npc_name}:[/{theme.NPC}] {text}")

    def system(self, text: str) -> None:
        self.console.print(f"[{theme.SYSTEM}]{text}[/{theme.SYSTEM}]")

    def error(self, text: str) -> None:
        self.console.print(f"[{theme.ERROR}]{text}[/{theme.ERROR}]")

    def meta(self, text: str) -> None:
        self.console.print(f"[{theme.META}]{text}[/{theme.META}]")

    def chapter_card(self, state: GameState, character: PlayableCharacter, anchor: StoryAnchor) -> None:
        body = (
            f"[bold]{character.display_name}[/bold]\n"
            f"{anchor.book} | {anchor.chapter}\n"
            f"{state.location}\n"
            f"{state.time_marker}"
        )
        self.console.print(Panel(body, title=anchor.label, border_style=theme.TITLE))

    def show_state(self, state: GameState) -> None:
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_row("Mode", state.game_mode.title())
        table.add_row("Location", state.location)
        table.add_row("Time", state.time_marker)
        table.add_row("Companions", ", ".join(state.companions) or "None")
        table.add_row("NPCs", ", ".join(state.npcs_present) or "None")
        table.add_row("Exits", ", ".join(state.available_exits) or "Unknown")
        if state.current_objective:
            table.add_row("Objective", state.current_objective)
        self.console.print(Panel(table, title="Present State", border_style=theme.SYSTEM))

    def show_options(self, title: str, options: list[str]) -> None:
        self.console.print(Panel("\n".join(options), title=title, border_style=theme.SYSTEM))

    def _stream(self, text: str, style: str) -> None:
        if self.config.reduced_motion or self.config.typewriter_delay <= 0:
            self.console.print(f"[{style}]{text}[/{style}]")
            return
        for paragraph in text.split("\n"):
            self.console.print(f"[{style}]{paragraph}[/{style}]")
            time.sleep(self.config.typewriter_delay)
