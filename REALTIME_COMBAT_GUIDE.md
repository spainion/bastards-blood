# User Accounts, Real-time Gameplay, Combat & Enemies Guide

Complete guide to user accounts, database persistence, real-time gameplay with WebSockets, combat system, and enemy/mob management.

## Table of Contents

- [User Accounts & Authentication](#user-accounts--authentication)
- [Database System](#database-system)
- [Real-time Gameplay with WebSockets](#real-time-gameplay-with-websockets)
- [Combat System](#combat-system)
- [Enemies & Mobs](#enemies--mobs)
- [Skills in Combat](#skills-in-combat)

---

## User Accounts & Authentication

### Features

- **User Registration**: Create accounts with username, email, password
- **JWT Authentication**: Secure token-based authentication
- **User Profiles**: Manage user data and settings
- **Character Ownership**: Link characters to user accounts
- **Role-based Access**: User and admin roles

### API Endpoints

#### Register User
```bash
POST /api/v1/users/register
Content-Type: application/json

{
  "username": "player1",
  "email": "player1@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "player1",
    "email": "player1@example.com",
    "is_active": true,
    "is_admin": false,
    "created_at": "2025-10-30T12:00:00Z"
  }
}
```

#### Login
```bash
POST /api/v1/users/login
Content-Type: application/json

{
  "username": "player1",
  "password": "securepassword123"
}
```

#### Get Current User
```bash
GET /api/v1/users/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Using Authentication

All authenticated endpoints require JWT token in header:
```bash
Authorization: Bearer <your_token_here>
```

---

## Database System

### Features

- **SQLAlchemy ORM**: Object-relational mapping for databases
- **SQLite Support**: Default embedded database (no setup)
- **PostgreSQL/MySQL Support**: Production-ready databases
- **Automatic Migrations**: Database schema auto-created on startup

### Database Models

**Users**: User accounts with authentication
**Characters**: Player characters with stats, inventory, skills
**Enemies**: Mobs and enemies with AI and loot
**CombatLogs**: Complete combat history
**GameSessions**: Active gameplay sessions

### Configuration

Set database URL in `.env`:

```bash
# SQLite (default)
DATABASE_URL=sqlite:///./bastards_blood.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/bastards_blood

# MySQL
DATABASE_URL=mysql://user:password@localhost/bastards_blood
```

### Character Persistence

Characters are now automatically saved to database with:
- Owner linkage (user_id)
- Full stats and inventory
- Location tracking
- Skill progression
- Equipment state

---

## Real-time Gameplay with WebSockets

### Features

- **Real-time Updates**: Instant push notifications for game events
- **Player Movement**: See other players move in real-time
- **Combat Updates**: Live combat action notifications
- **Chat System**: Real-time chat between players
- **NPC Interactions**: See when others interact with NPCs

### WebSocket Connection

Connect to WebSocket endpoint:

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/ws/connection-123?user_id=1&session_id=game-001`
);

// Handle connection
ws.onopen = () => {
  console.log("Connected to game server");
};

// Handle messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received:", message);
};
```

### Message Types

#### Ping/Pong (Keep-alive)
```json
{
  "type": "ping"
}
```

#### Player Movement
```json
{
  "type": "movement",
  "location": {"x": 100, "y": 200, "z": 0}
}
```

#### Combat Action
```json
{
  "type": "combat_action",
  "attacker_id": "char-hero",
  "action": "attack",
  "result": {"damage": 25, "critical": true}
}
```

#### Chat Message
```json
{
  "type": "chat",
  "message": "Hello everyone!"
}
```

### Receiving Updates

Server broadcasts events to connected players:

```json
{
  "type": "player_moved",
  "user_id": 2,
  "location": {"x": 150, "y": 250, "z": 0},
  "timestamp": "2025-10-30T12:30:00Z"
}
```

```json
{
  "type": "combat_update",
  "attacker_id": "char-hero",
  "action": "attack",
  "result": {"damage": 30, "critical": false},
  "timestamp": "2025-10-30T12:30:15Z"
}
```

---

## Combat System

### Features

- **Damage Calculation**: Base damage + stat modifiers + skill bonuses
- **Critical Hits**: 5% chance for 2x damage
- **Miss Chance**: 5% chance to miss
- **Armor Mitigation**: Reduces damage based on armor rating
- **Combat Log**: Full history of all combat actions
- **XP Rewards**: Gain XP from defeating enemies
- **Loot System**: Random loot drops from enemies

### Combat Flow

1. Player initiates attack on enemy
2. System calculates damage with rolls
3. Armor mitigation applied
4. HP updated for both combatants
5. Check if defender defeated
6. Award XP and loot if applicable
7. Log combat action
8. Broadcast to real-time players

### Damage Calculation

```
Base Damage = Random(damage_min, damage_max)
STR Bonus = (STR - 10)
Skill Bonus = Skill level / 10
Total Pre-Armor = Base + STR Bonus + Skill Bonus
Armor Reduction = min(Armor * 0.5, Total * 0.75)
Final Damage = max(1, Total - Armor Reduction)
```

### Attack Enemy

```bash
POST /api/v1/combat/attack
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "game-001",
  "attacker_id": "char-hero",
  "defender_id": "enemy-goblin-001",
  "action_type": "attack",
  "data": {
    "damage_min": 10,
    "damage_max": 20,
    "skill_bonus": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "damage_dealt": 18,
  "damage_type": "physical",
  "was_critical": false,
  "was_miss": false,
  "attacker_hp": {"max": 100, "current": 100},
  "defender_hp": {"max": 50, "current": 32},
  "defender_defeated": false,
  "xp_gained": 0,
  "loot_dropped": [],
  "message": "char-hero dealt 18 damage to enemy-goblin-001",
  "details": [
    "Damage roll: 18",
    "Armor mitigation: 5",
    "Defender HP: 50 -> 32"
  ]
}
```

### Get Combat Log

```bash
GET /api/v1/combat/combat-log/game-001?limit=20
Authorization: Bearer <token>
```

---

## Enemies & Mobs

### Features

- **10 Enemy Templates**: Pre-defined enemy types
- **Level Scaling**: Stats scale with level
- **AI Behaviors**: Aggressive, passive, patrol, flee
- **Loot Tables**: Customizable drop rates
- **Respawn System**: Automatic respawn after death
- **Spawn Management**: Create enemies at specific locations

### Enemy Types

| Template | Type | Base Level | HP | Damage | XP |
|----------|------|------------|-----|--------|-----|
| goblin | Goblin | 5 | 30 | 5 | 25 |
| orc | Orc | 15 | 100 | 15 | 75 |
| troll | Troll | 25 | 250 | 30 | 200 |
| skeleton | Undead | 10 | 50 | 10 | 50 |
| zombie | Undead | 12 | 80 | 12 | 60 |
| demon | Demon | 40 | 600 | 75 | 750 |
| wolf | Beast | 8 | 40 | 8 | 35 |
| bear | Beast | 20 | 200 | 25 | 150 |
| dragon | Dragon | 50 | 1000 | 100 | 1000 |
| boss_demon_lord | Boss | 75 | 5000 | 200 | 5000 |

### Spawn Enemies

```bash
POST /api/v1/combat/spawn-enemy
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "game-001",
  "enemy_template": "goblin",
  "location": {"x": 150, "y": 250, "z": 0},
  "region": "Dark Forest",
  "level_override": 10,
  "quantity": 5
}
```

**Response:**
```json
[
  "enemy-goblin-1730280000-0",
  "enemy-goblin-1730280000-1",
  "enemy-goblin-1730280000-2",
  "enemy-goblin-1730280000-3",
  "enemy-goblin-1730280000-4"
]
```

### List Enemies

```bash
GET /api/v1/combat/enemies?session_id=game-001&region=Dark Forest&alive_only=true
Authorization: Bearer <token>
```

### Get Enemy Templates

```bash
GET /api/v1/combat/enemy-templates
```

---

## Skills in Combat

### Combat Skills

The progressive skills system integrates with combat:

**Attack** - Increases melee damage
**Strength** - Increases damage multiplier
**Defence** - Reduces incoming damage
**Ranged** - Improves ranged attacks
**Magic** - Enhances spell damage
**Hitpoints** - Increases max HP
**Prayer** - Provides combat buffs

### Skill Bonuses in Combat

- +1 damage per 10 Attack levels
- +1 armor per 10 Defence levels
- Higher success rates on special attacks
- Unlock powerful abilities at milestones

### Combat Level

Calculated from combat skills:
```
Combat Level = (Attack + Strength + Defence) * 0.25 
             + Hitpoints * 0.25 
             + Prayer * 0.125 
             + (Magic + Ranged) * 0.125
```

### Training Combat Skills

Gain XP through combat:
- Attack XP: +10 per successful hit
- Strength XP: +10 per damage dealt / 10
- Defence XP: +5 per hit taken (survived)
- Hitpoints XP: +5 per damage dealt / 10

---

## Complete Example Workflow

### 1. Register and Login

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(f"{BASE_URL}/api/v1/users/register", json={
    "username": "player1",
    "email": "player1@example.com",
    "password": "password123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

### 2. Create Character

```python
character = {
    "id": "char-warrior",
    "name": "Mighty Warrior",
    "class": "Warrior",
    "lvl": 10,
    "stats": {"STR": 18, "DEX": 12, "CON": 16, "INT": 8, "WIS": 10, "CHA": 10},
    "hp": {"max": 120, "current": 120},
    "location": {"x": 100, "y": 100, "z": 0}
}
requests.post(f"{BASE_URL}/api/v1/characters", headers=headers, json=character)
```

### 3. Spawn Enemies

```python
spawn_request = {
    "session_id": "game-001",
    "enemy_template": "goblin",
    "location": {"x": 150, "y": 150, "z": 0},
    "quantity": 3
}
response = requests.post(f"{BASE_URL}/api/v1/combat/spawn-enemy", 
                        headers=headers, json=spawn_request)
enemy_ids = response.json()
```

### 4. Attack Enemy

```python
attack = {
    "session_id": "game-001",
    "attacker_id": "char-warrior",
    "defender_id": enemy_ids[0],
    "action_type": "attack",
    "data": {"damage_min": 15, "damage_max": 25, "skill_bonus": 2}
}
result = requests.post(f"{BASE_URL}/api/v1/combat/attack",
                      headers=headers, json=attack)
print(result.json())
```

### 5. Connect WebSocket

```javascript
const ws = new WebSocket(
  `ws://localhost:8000/ws/conn-123?user_id=1&session_id=game-001`
);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === "combat_update") {
    console.log(`Combat: ${msg.message}`);
  }
};
```

---

## Summary

This comprehensive system provides:

✅ **User Accounts** - Registration, login, JWT authentication
✅ **Database** - Persistent storage for all game data  
✅ **Real-time** - WebSocket connections for live updates  
✅ **Combat** - Full damage calculation, criticals, misses  
✅ **Enemies** - 10 templates with level scaling and AI  
✅ **Skills** - Combat skills integrated with damage/defense  
✅ **Loot** - Random drops and XP rewards  
✅ **Logs** - Complete combat history tracking  

The system is production-ready and can scale to support:
- Thousands of concurrent players
- Multiple game sessions
- Complex combat scenarios
- Real-time multiplayer gameplay
