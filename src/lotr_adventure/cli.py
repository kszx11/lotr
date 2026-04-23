from __future__ import annotations

from lotr_adventure.config import Config
from lotr_adventure.engine.game import GameApp


def run() -> None:
    app = GameApp(Config.load())
    app.run()
