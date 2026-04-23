# Lord of the Rings Adventure Game Implementation Plan

## Goal

Build an immersive Python text adventure inspired by *The Lord of the Rings* books that uses the OpenAI API for:

- scene generation
- story flow and consequence handling
- in-character conversations with world NPCs
- structured world state updates

The game should let the player:

- choose different playable characters
- jump to different book locations and time points
- explore, inspect, travel, speak, and make choices
- remain inside the fiction at all times

## Reference Project Findings

The project in `/Users/kspringall/code/adventure` is a useful proof of concept for:

- terminal loop structure
- save/load flow
- ANSI colorized output
- command parsing
- OpenAI-backed scene narration
- dedicated NPC chat mode

It should not be copied as-is because it keeps nearly all logic in one file and relies on freeform model output for state extraction. For this project, we should keep the fast terminal ergonomics and replace the game engine with a more structured architecture.

## Product Direction

### Game style

- single-player terminal game
- strong book-tone narration
- immersive prose over puzzle-heavy parser gameplay
- command-driven exploration with optional menu hints
- lore-aware but bounded to the selected era, location, and viewpoint

### Core fantasy

The player steps into Middle-earth as a chosen viewpoint character and can enter specific places and moments from the books, then branch into alternate-but-lore-respecting adventures from that anchor point.

## Architecture

### 1. Terminal UI layer

Responsibility:

- render colored text smoothly
- animate output with optional typewriter speed
- accept commands and shortcuts
- show status panels for location, time, party, inventory, and active threads

Recommended libraries:

- `rich` for color, panels, layout, and markdown-ish prose rendering
- `prompt_toolkit` for history, completion, and better input handling

### 2. Game state layer

Responsibility:

- store canonical player state
- track current era, chapter anchor, location, inventory, companions, quests, and flags
- persist save files
- keep separate conversation threads for narrator and NPCs

Suggested model objects:

- `GameState`
- `PlayerCharacter`
- `StoryAnchor`
- `LocationState`
- `NpcState`
- `QuestState`
- `ConversationState`

### 3. Lore layer

Responsibility:

- define canon-safe starting anchors
- define available playable characters
- define major locations, factions, and era metadata
- supply grounding data to prompts before generation

This should start as local JSON or YAML content rather than an external database.

### 4. AI orchestration layer

Responsibility:

- call OpenAI for narrator turns
- call OpenAI for NPC chat
- request structured state deltas after player actions
- enforce style and canon boundaries through prompt design

Split the model roles:

- `Narrator engine`: vivid scene writing, action outcomes, choices, tone
- `State engine`: structured JSON describing changes to world/player state
- `NPC engine`: first-person in-character chat with memory and knowledge limits

### 5. Rules and safety layer

Responsibility:

- prevent characters from breaking immersion
- restrict knowledge to in-world facts
- stop the narrator from referencing the real world or the model
- reject out-of-scope jumps not unlocked by the current campaign mode

## OpenAI Integration Strategy

### API choice

Use the OpenAI Responses API for new development, not the older chat-only pattern used by the reference project.

### Why

- cleaner multi-turn state handling
- better fit for separate narrator and NPC threads
- easier structured outputs for state updates
- better path for future streaming output

### Request types

1. Narration request
   Generate the prose response to the player's command.

2. State update request
   Return strict JSON with location changes, inventory deltas, quest updates, NPC affinity changes, discovered facts, and suggested exits.

3. NPC dialogue request
   Keep a character-specific conversation thread with tight instructions about voice, era, and knowledge boundaries.

4. Hint request
   Offer subtle in-world guidance without exposing system mechanics.

## Proposed Repository Layout

```text
lotr/
  IMPLEMENTATION_PLAN.md
  README.md
  requirements.txt
  .env.example
  src/
    lotr_adventure/
      __init__.py
      main.py
      cli.py
      config.py
      engine/
        game.py
        commands.py
        saves.py
        router.py
      ai/
        client.py
        narrator.py
        npc_chat.py
        state_updates.py
        prompts.py
        schemas.py
      domain/
        models.py
        lore.py
        anchors.py
      ui/
        render.py
        theme.py
        input.py
      content/
        playable_characters.yaml
        story_anchors.yaml
        locations.yaml
        prompt_fragments/
```

## Play Flow

### New game

1. Choose a playable character.
2. Choose a story anchor.
3. Load initial lore pack for that era and location.
4. Generate opening scene.
5. Enter main command loop.

### Main turn loop

1. Parse the player command.
2. Route to local action, travel action, jump action, inspection, dialogue, or meta command.
3. Build the AI prompt from:
   - current state
   - local lore facts
   - recent summary
   - current objective threads
   - command intent
4. Generate narrator output.
5. Generate structured state delta.
6. Validate and apply the delta.
7. Render the updated world state.
8. Save autosave snapshot.

### NPC conversation loop

1. Enter character chat mode with one NPC.
2. Bind a system/developer prompt specific to that NPC identity.
3. Include only knowledge the NPC should plausibly know.
4. Preserve a short rolling memory for that conversation.
5. Exit back to main loop on farewell or command prefix.

## Command Set

Initial command set:

- `look`
- `go <place>`
- `travel <place>`
- `jump <anchor>`
- `talk <character>`
- `ask <character> about <topic>`
- `inspect <object>`
- `inventory`
- `journal`
- `party`
- `map`
- `where`
- `help`
- `save`
- `load`
- `quit`

The `jump` command should be limited by explicit story-anchor definitions so the game remains coherent.

## Lore and Canon Strategy

The game should be "book-faithful from a chosen anchor," not a fully unconstrained Middle-earth simulator.

Rules:

- prompts should mention the tone, setting, and social assumptions of Tolkien's world
- characters speak with period-appropriate diction, but still remain readable
- NPCs know only what they would know from place, station, and timeline
- no references to modern concepts, AI, game systems, or the reader
- alternate outcomes are allowed after the chosen anchor, but should stay lore-respecting

## Structured Output Plan

Do not trust freeform text to mutate game state.

For each player action that can change the world, request a strict JSON payload containing fields like:

- `location`
- `time_marker`
- `inventory_add`
- `inventory_remove`
- `companions_present`
- `quests_updated`
- `npc_relationship_changes`
- `facts_learned`
- `available_exits`
- `danger_level`
- `should_trigger_battle`

Validate this schema in Python before applying it.

## Save System

Use JSON save files at first.

Store:

- player profile
- chosen anchor
- current state
- known NPCs
- discovered lore facts
- narration summaries
- active response thread IDs if we decide to persist them

Maintain:

- `savegame.json`
- `autosave.json`

## Color and UX Direction

Use color intentionally, not just everywhere.

- gold for narration headings and chapter cards
- green for travel and discovery
- blue or cyan for system hints and location metadata
- red for danger or failed actions
- dim styling for recaps and memory summaries

Add:

- chapter title cards
- smooth line-by-line rendering
- optional reduced-motion mode
- clear separation between narrator prose and NPC speech

## Build Phases

### Phase 1: Foundation

- scaffold package structure
- config loading
- OpenAI client wrapper
- terminal UI shell
- basic command parser
- save/load support

### Phase 2: Lore-driven exploration

- playable characters data
- story anchors data
- location metadata
- narrator prompts
- travel and look commands

### Phase 3: Character chat

- NPC identity model
- NPC prompt templates
- conversation state storage
- in-character enforcement

### Phase 4: Structured state and consequences

- JSON schemas
- validation layer
- inventory, quests, and relationship changes
- autosave and summaries

### Phase 5: Polish

- richer output styling
- better help and onboarding
- balancing prompt costs
- test coverage

## Broad-Completion Baseline

The project has now reached the practical finish line for an initial release:

- Story Mode and Open Mode are both implemented and usable.
- Major arcs from *The Hobbit* and *The Lord of the Rings* are covered by playable canon viewpoints.
- Lore-backed locations, anchors, and NPC profiles are broad enough to support immersive play without further architectural work.

From this point, the default policy is:

- treat content as **frozen at a broadly complete baseline**
- add new scenes only to close a specific identified gap
- prioritize polish, playtesting, packaging, prompt tuning, and release readiness over open-ended expansion

## Testing Plan

### Unit tests

- command parsing
- state mutation
- schema validation
- save/load round trips

### Integration tests

- scripted travel flow
- NPC chat entry and exit
- jump between anchors
- autosave restore

### Prompt contract tests

- narrator output remains immersive
- NPC replies stay in character
- structured state payload validates
- forbidden real-world references are rejected

## First Implementation Slice

The fastest useful first version should be:

1. terminal app with `rich` + `prompt_toolkit`
2. choose one of three playable characters
3. choose one of three story anchors
4. support `look`, `go`, `talk`, `jump`, `save`, `load`
5. narrator output via OpenAI
6. NPC chat via OpenAI
7. structured JSON state updates

Suggested first anchors:

- Frodo in the Shire before departure
- Aragorn at Bree during the hobbits' arrival
- Sam in Ithilien during the journey to Mordor

## Questions To Resolve Before Coding

1. Do you want us to stay strictly with material from *The Fellowship of the Ring*, *The Two Towers*, and *The Return of the King*, or also include *The Hobbit* and appendices?
2. Are alternate-history branches allowed after a player jumps into a canon scene, or do you want the game to keep returning toward book-canon outcomes?
3. Should playable characters be limited to named canon characters at first, or should we also allow original characters in Middle-earth?
4. Do you want combat in the first version, or should the first release focus on exploration, dialogue, travel, and consequence?
5. For the first build, should jumping be unrestricted from the menu, or only available after unlocking story anchors through play?
