from __future__ import annotations

from lotr_adventure.domain.models import ParsedCommand


def parse_command(raw: str) -> ParsedCommand:
    text = raw.strip()
    lowered = text.lower()

    if not text:
        return ParsedCommand(kind="empty", raw=raw)
    if lowered in {"quit", "exit"}:
        return ParsedCommand(kind="quit", raw=raw)
    if lowered in {"menu", "main menu"}:
        return ParsedCommand(kind="menu", raw=raw)
    if lowered in {"help", "?"}:
        return ParsedCommand(kind="help", raw=raw)
    if lowered in {"look", "observe"}:
        return ParsedCommand(kind="look", raw=raw)
    if lowered in {"inventory", "inv"}:
        return ParsedCommand(kind="inventory", raw=raw)
    if lowered == "journal":
        return ParsedCommand(kind="journal", raw=raw)
    if lowered in {"objective", "objectives"}:
        return ParsedCommand(kind="objective", raw=raw)
    if lowered in {"hint", "hints", "suggest", "suggestion", "suggestions", "what now", "next step"}:
        return ParsedCommand(kind="hint", raw=raw)
    if lowered in {"story", "story mode"}:
        return ParsedCommand(kind="story_status", raw=raw)
    if lowered in {"continue", "continue story", "next", "next chapter"}:
        return ParsedCommand(kind="continue_story", raw=raw)
    if lowered == "party":
        return ParsedCommand(kind="party", raw=raw)
    if lowered == "where":
        return ParsedCommand(kind="where", raw=raw)
    if lowered == "map":
        return ParsedCommand(kind="map", raw=raw)
    if lowered == "save":
        return ParsedCommand(kind="save", raw=raw)
    if lowered == "load":
        return ParsedCommand(kind="load", raw=raw)
    if lowered == "jump":
        return ParsedCommand(kind="jump_menu", raw=raw)

    for prefix in ("go to ", "travel to ", "move to ", "head to ", "go ", "travel "):
        if lowered.startswith(prefix):
            return ParsedCommand(kind="travel", raw=raw, target=text[len(prefix):].strip())

    if lowered.startswith("jump "):
        return ParsedCommand(kind="jump", raw=raw, target=text[5:].strip())

    for prefix in ("inspect ", "examine ", "look at "):
        if lowered.startswith(prefix):
            return ParsedCommand(kind="inspect", raw=raw, target=text[len(prefix):].strip())

    for prefix in ("talk to ", "talk ", "chat with ", "speak with "):
        if lowered.startswith(prefix):
            return ParsedCommand(kind="talk", raw=raw, target=text[len(prefix):].strip())

    if lowered.startswith("ask "):
        rest = text[4:].strip()
        split = rest.lower().split(" about ", maxsplit=1)
        if len(split) == 2:
            name = rest[: rest.lower().index(" about ")].strip()
            topic = rest[rest.lower().index(" about ") + 7 :].strip()
            return ParsedCommand(kind="ask", raw=raw, target=name, topic=topic)

    return ParsedCommand(kind="unknown", raw=raw, target=text)
