from __future__ import annotations

import json
from pathlib import Path

from lotr_adventure.domain.models import GameState


def save_state(path: Path, state: GameState) -> None:
    path.write_text(json.dumps(state.to_dict(), indent=2))


def load_state(path: Path) -> GameState:
    data = json.loads(path.read_text())
    return GameState.from_dict(data)
