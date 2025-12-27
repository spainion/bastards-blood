# Bastards Blood GPT Integration

This document provides instructions for setting up a Custom GPT to interact with the Bastards Blood RPG data store.

## Overview

The Bastards Blood repository uses GitHub Actions workflows to enable GPT-powered game management. A Custom GPT can:

1. **Read game data** - View characters, sessions, and game state
2. **Create characters** - Add new characters to the campaign
3. **Manage sessions** - Create and track game sessions
4. **Log events** - Record gameplay events
5. **Execute actions** - Roll dice, attack, cast spells, etc.

## Setup Instructions

### 1. Create a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Create a new token with these permissions for the `spainion/bastards-blood` repository:
   - **Contents**: Read and write
   - **Pull requests**: Read and write
   - **Actions**: Read and write (for triggering workflows)
3. Copy the token for use in the GPT configuration

### 2. Create Custom GPT

1. Go to [chat.openai.com](https://chat.openai.com) and create a new GPT
2. Configure the GPT with the instructions below
3. Add the OpenAPI schema from `gpt-actions/openapi-schema.json`
4. Set up authentication using your GitHub token

### 3. GPT Instructions

Use these instructions when creating your Custom GPT:

```
You are a Game Master assistant for the Bastards Blood tabletop RPG campaign. You help manage game state stored in a GitHub repository.

## Your Capabilities

1. **View Data**: Read characters, sessions, and game state from the repository
2. **Create Characters**: Add new characters using the add-character workflow
3. **Manage Sessions**: Create new sessions and log gameplay events
4. **Execute Actions**: Run gameplay actions like dice rolls, attacks, and spells

## Workflow Triggers

To trigger workflows, use the repository dispatch endpoint:
POST /repos/spainion/bastards-blood/dispatches

With event_type set to one of:
- "add-character" - Create a new character (creates a PR)
- "update-character" - Update existing character (creates a PR)
- "create-session" - Start a new game session
- "log-event" - Log a gameplay event to a session
- "gameplay-action" - Execute a gameplay action (roll, attack, etc.)
- "get-state" - Calculate current game state
- "chatgpt-helper" - Get repository status and info

## Event Types

When logging events, use these types:
- note: General narrative notes
- check: Ability checks or skill rolls
- attack: Attack rolls
- damage: Damage dealt
- heal: Healing received
- gain_item: Item acquired
- lose_item: Item lost/used
- status: Status effect applied/removed
- create_char: Character creation
- update_char: Character modification
- custom: Any other event type

## Gameplay Actions

Available gameplay actions:
- roll: Roll dice (params: dice="1d20", stat="STR")
- attack: Make an attack (params: attack_stat="STR", damage_dice="1d8")
- cast_spell: Cast a spell (params: spell_name, spell_level, effect_dice)
- use_item: Use an item (params: item_name, effect_dice)
- rest: Take a rest (params: rest_type="short" or "long")
- travel: Travel to location (params: destination, distance)

## Response Guidelines

1. Always confirm actions before triggering workflows
2. Provide clear feedback on action results
3. Maintain game continuity and narrative consistency
4. Track character HP and resources across sessions
5. Roll dice and apply game mechanics fairly
```

## API Examples

### Add a Character

```json
POST /repos/spainion/bastards-blood/dispatches
{
  "event_type": "add-character",
  "client_payload": {
    "character_id": "char-gareth",
    "character_name": "Gareth Ironforge",
    "character_class": "Fighter",
    "level": 3,
    "str": 16,
    "dex": 12,
    "con": 14,
    "int": 10,
    "wis": 11,
    "cha": 8,
    "hp_max": 28,
    "inventory": "longsword,shield,chainmail",
    "tags": "party,tank",
    "notes": "Dwarf fighter from the mountain holds"
  }
}
```

### Create a Session

```json
POST /repos/spainion/bastards-blood/dispatches
{
  "event_type": "create-session",
  "client_payload": {
    "campaign": "bastards-blood",
    "session_date": "2025-01-15"
  }
}
```

### Execute a Gameplay Action

```json
POST /repos/spainion/bastards-blood/dispatches
{
  "event_type": "gameplay-action",
  "client_payload": {
    "action_type": "attack",
    "session_id": "2025-01-15-0001",
    "actor": "char-akira",
    "target": "goblin-chief",
    "parameters": {
      "attack_stat": "DEX",
      "damage_dice": "1d6+3"
    }
  }
}
```

### Log an Event

```json
POST /repos/spainion/bastards-blood/dispatches
{
  "event_type": "log-event",
  "client_payload": {
    "session_id": "2025-01-15-0001",
    "event_type": "note",
    "actor": "gm",
    "event_data": "{\"text\": \"The party enters the ancient tomb...\"}"
  }
}
```

## Available Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `add-character.yml` | `add-character` | Create new character (via PR) |
| `update-character.yml` | `update-character` | Modify character (via PR) |
| `create-session.yml` | `create-session` | Create new game session |
| `log-event.yml` | `log-event` | Log event to session |
| `gameplay-action.yml` | `gameplay-action` | Execute gameplay action |
| `get-state.yml` | `get-state` | Calculate game state |
| `chatgpt-helper.yml` | `chatgpt-helper` | Get repo status/info |
| `validate.yml` | Pull Request | Validate JSON schemas |

## Data Schemas

### Character Schema
- `id`: Unique identifier (lowercase, alphanumeric with dashes)
- `name`: Display name
- `class`: Character class
- `lvl`: Level (integer)
- `stats`: Object with STR, DEX, CON, INT, WIS, CHA
- `hp`: Object with max and current
- `inventory`: Array of item strings
- `tags`: Array of tag strings
- `notes`: Backstory/notes string

### Session Schema
- `id`: Session ID (YYYY-MM-DD-NNNN format)
- `campaign`: Campaign name
- `events`: Array of event objects

### Event Schema
- `id`: Event ID (e_XXXXXXXX format)
- `ts`: ISO 8601 timestamp
- `t`: Event type
- `actor`: Actor character ID (optional)
- `target`: Target character ID (optional)
- `data`: Event data object (optional)
- `result`: Event result object (optional)
