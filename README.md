# Lord of the Rings Adventure

An immersive terminal adventure in Python set in Middle-earth, using the OpenAI API for:

- scene narration
- lore-aware game flow
- in-character NPC dialogue
- structured world-state updates

The game leans toward the books' canon, supports named canon protagonists, and lets you jump directly to major story anchors from *The Hobbit* and *The Lord of the Rings*.

## Features

- colored terminal UI with `rich`
- command input with optional `prompt_toolkit`
- playable canon characters
- jumpable story anchors across books
- in-character NPC chat engine
- lore-grounded location and NPC profiles
- persistent NPC memory and relationship tracking
- Story Mode with guided chapter progression
- Open Mode with freer anchor jumping
- in-world `hint` guidance tied to the active chapter
- save/load and autosave
- structured state updates validated in Python

## Status

The project is now in a **broadly complete content baseline** state.

- Major arcs from *The Hobbit* and *The Lord of the Rings* are playable in Story Mode and Open Mode.
- Remaining work should be treated as polish, testing, prompt tuning, and selective scene refinement.
- New content should only be added to close a clearly identified gap, not to restart open-ended corpus expansion.

## Setup

1. Create a virtual environment.
2. Install dependencies.
3. Set `OPENAI_API_KEY`.
4. Run the game.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
python -m lotr_adventure
```

If your local `pip` is older, `python -m pip install -e .` is preferred.
If editable install still fails because `pip` lacks wheel/build support, use `python setup.py develop`.
At startup, the game offers `Resume autosave` when an autosave is present, and `Load savegame` when you have created a manual save.

## Environment

```env
OPENAI_API_KEY=your_key_here
OPENAI_TEXT_MODEL=gpt-4.1-mini
OPENAI_STRUCTURED_MODEL=gpt-4o-mini
```

## Commands

- `look`
- `go <place>`
- `travel <place>`
- `inspect <thing>`
- `talk <character>`
- `ask <character> about <topic>`
- `jump <anchor id or words>`
- `where`
- `map`
- `objective`
- `hint`
- `story`
- `continue`
- `inventory`
- `journal`
- `party`
- `save`
- `load`
- `help`
- `quit`

## Notes

- `jump` is always available.
- In Story Mode, `jump` is limited to chapters already opened on the active story path.
- If you jump to an anchor tied to a different protagonist, the game switches viewpoint to that canon character.
- If the OpenAI API is unavailable, the game stays playable with a minimal local fallback narrator.
- Travel now uses local location metadata and known linked routes before asking the model to elaborate the scene.
- Story Mode now advances only after chapter-specific conversations, inspections, travel, or learned facts have been satisfied.
- Current authored paths now include expanded Bilbo and Gandalf arcs in addition to the existing Frodo, Sam, and Aragorn storylines.
- The current content baseline is intentionally frozen at a broad-coverage milestone so future work can focus on quality and release readiness.
- `save` writes a deliberate manual milestone to `savegame.json`, while scene changes refresh `autosave.json`.
