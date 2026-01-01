# Bastards Blood Data Store

This repo stores RPG state as JSON plus append-only session event logs.
Edit via pull requests only. CI validates schemas.

## 🎮 GPT Integration

This repository is fully integrated with ChatGPT Custom GPTs for AI-powered game management.

### Quick Start for GPT

1. See [GPT Setup Guide](gpt-actions/GPT-SETUP.md) for Custom GPT configuration
2. Use the [OpenAPI Schema](gpt-actions/openapi-schema.json) for action definitions
3. Trigger workflows via GitHub's repository dispatch API

### Available GPT Actions

#### Core Gameplay
| Action | Description |
|--------|-------------|
| `add-character` | Create a new character (via PR) |
| `update-character` | Modify an existing character (via PR) |
| `create-session` | Start a new game session |
| `log-event` | Log gameplay events to a session |
| `gameplay-action` | Execute game actions (roll, attack, spell, etc.) |
| `get-state` | Calculate current game state |
| `chatgpt-helper` | Get repository status and info |

#### Advanced Operations
| Action | Description |
|--------|-------------|
| `gpt-file-ops` | Read, create, update, delete files |
| `gpt-query` | Query characters, sessions, game state |
| `gpt-batch` | Bulk operations (damage, heal, items) |
| `gpt-combat` | Combat management (initiative, turns) |
| `gpt-narrative` | Log narrative and story content |
| `gpt-world` | World building (locations, NPCs, items) |
| `gpt-sync` | Export, backup, validate data |
| `gpt-agent-task` | AI-powered analysis and suggestions |
| `gpt-workspace` | Build workspace bundle and manifest |

#### Memory & AI Integration
| Action | Description |
|--------|-------------|
| `gpt-memory` | Persistent memory storage and retrieval |
| `gpt-context` | Context window management for LLM |
| `gpt-prompt` | Prompt engineering and templates |
| `gpt-knowledge` | Semantic search knowledge base |

### Gameplay Actions

- **roll** - Roll dice with optional stat modifiers
- **attack** - Make attack rolls with damage
- **cast_spell** - Cast spells with effects
- **use_item** - Use inventory items
- **rest** - Short or long rest for healing
- **travel** - Travel with encounter checks

## Layout

```
schemas/           # JSON schemas for validation
  character.schema.json
  event.schema.json
  session.schema.json
data/
  characters/      # Character JSON files
  sessions/        # Session event logs
scripts/           # Python automation scripts
gpt-actions/       # GPT integration files
  openapi-schema.json
  GPT-SETUP.md
.github/workflows/ # GitHub Actions for automation
```

## Scripts

| Script | Purpose |
|--------|---------|
| `reduce_state.py` | Calculate state from session events |
| `create_character.py` | Create new character files |
| `update_character.py` | Update existing characters |
| `create_session.py` | Create new session files |
| `log_event.py` | Append events to sessions |
| `get_game_state.py` | Get computed game state |
| `gameplay_action.py` | Execute gameplay mechanics |
| `query_data.py` | Query and search game data |
| `batch_operations.py` | Bulk character operations |
| `combat_manager.py` | Combat tracking and management |
| `log_narrative.py` | Log narrative content |
| `world_builder.py` | Create world content |
| `data_sync.py` | Export and backup data |
| `agent_tasks.py` | AI-powered game assistance |
| `memory_store.py` | Persistent memory storage |
| `context_engine.py` | LLM context management |
| `prompt_engine.py` | Prompt templates and chains |
| `openrouter_client.py` | Minimal OpenRouter chat helper (dev) |
| `dev_openrouter_workbench.py` | Run context + prompts through OpenRouter (dev) |
| `knowledge_base.py` | Semantic search and indexing |

## Schemas

### Character
```json
{
  "id": "char-name",
  "name": "Display Name",
  "class": "Fighter",
  "lvl": 1,
  "stats": { "STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10 },
  "hp": { "max": 10, "current": 10 },
  "inventory": ["item1", "item2"],
  "tags": ["party"],
  "notes": "Character backstory"
}
```

### Event Types
- `note` - Narrative notes
- `check` - Skill/ability checks
- `attack` - Attack rolls
- `damage` - Damage dealt
- `heal` - Healing received
- `gain_item` / `lose_item` - Inventory changes
- `status` - Status effects
- `create_char` / `update_char` - Character changes
- `custom` - Custom events

## CI Validation

All pull requests automatically validate JSON files against schemas using `ajv-cli`.
