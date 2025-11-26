# Admin Dashboard & In-Game Editing Guide

Complete guide for administrators to manage the RPG server, edit game state in real-time, and monitor multiplayer sessions.

## Table of Contents

1. [Admin Authentication](#admin-authentication)
2. [Server Statistics](#server-statistics)
3. [In-Game Editing](#in-game-editing)
4. [Player Management](#player-management)
5. [Session Management](#session-management)
6. [Real-Time Monitoring](#real-time-monitoring)
7. [Admin Actions Reference](#admin-actions-reference)

---

## Admin Authentication

### Setting Up Admin Accounts

Admin accounts must have the `role` field set to `"admin"` in the database.

**Create Admin User:**
```python
from api.database import SessionLocal, User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
admin_user = User(
    username="admin",
    email="admin@example.com",
    hashed_password=pwd_context.hash("secure_admin_password"),
    role="admin"  # Important!
)
db.add(admin_user)
db.commit()
```

**Login as Admin:**
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_admin_password"
  }'

# Response includes JWT token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

Use the `access_token` in subsequent requests:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Server Statistics

### Get Server Overview

**Endpoint:** `GET /api/v1/admin/stats`

**Requires:** Admin authentication

```bash
curl http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response:**
```json
{
  "total_users": 150,
  "active_sessions": 12,
  "online_players": 45,
  "total_characters": 203,
  "total_npcs": 75,
  "total_enemies": 120,
  "database_size": "125MB",
  "uptime_seconds": 86400,
  "websocket_connections": 45
}
```

### Session Statistics

Get detailed stats for a specific session:

```bash
curl http://localhost:8000/api/v1/admin/session/game-001/stats \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response:**
```json
{
  "session_id": "game-001",
  "player_count": 8,
  "npc_count": 15,
  "enemy_count": 23,
  "events_count": 1523,
  "duration_seconds": 7200,
  "top_players": [
    {"character_id": "char-001", "level": 45, "total_xp": 125000},
    {"character_id": "char-002", "level": 42, "total_xp": 110000}
  ]
}
```

---

## In-Game Editing

### Spawn Entities

**Endpoint:** `POST /api/v1/admin/spawn-entity`

Spawn enemies, NPCs, or items at any location.

**Spawn Enemies:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/spawn-entity \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "entity_type": "enemy",
    "template_id": "dragon",
    "location": {"x": 100, "y": 200, "z": 0},
    "quantity": 3,
    "custom_properties": {
      "level": 50,
      "aggressive": true
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "spawned": [
    {
      "id": "enemy-dragon-001",
      "name": "Dragon",
      "level": 50,
      "location": {"x": 100, "y": 200, "z": 0}
    },
    // ... 2 more dragons
  ],
  "count": 3
}
```

**Spawn NPCs:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/spawn-entity \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "entity_type": "npc",
    "template_id": "merchant",
    "location": {"x": 50, "y": 50, "z": 0},
    "quantity": 1,
    "custom_properties": {
      "name": "Mysterious Trader",
      "dialogue": {
        "greeting": ["Greetings, traveler!", "I have rare wares!"]
      }
    }
  }'
```

**Spawn Items:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/spawn-entity \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "entity_type": "item",
    "template_id": "legendary_sword",
    "location": {"x": 75, "y": 100, "z": 0},
    "quantity": 1
  }'
```

### Modify Character

**Endpoint:** `POST /api/v1/admin/modify-character`

Change any character property in real-time.

**Give Items:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/modify-character \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char-hero",
    "modifications": {
      "inventory": [
        {"id": "sword-legendary", "name": "Legendary Sword", "type": "weapon"},
        {"id": "potion-health", "name": "Health Potion", "type": "consumable"}
      ]
    },
    "notify_player": true
  }'
```

**Modify Stats:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/modify-character \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char-hero",
    "modifications": {
      "stats": {"STR": 25, "DEX": 20, "CON": 18},
      "lvl": 50,
      "hp": {"max": 500, "current": 500}
    },
    "notify_player": true
  }'
```

**Give Currency:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/modify-character \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char-hero",
    "modifications": {
      "currency": {"gold": 10000, "silver": 5000}
    },
    "notify_player": true
  }'
```

### Teleport Player

**Endpoint:** `POST /api/v1/admin/teleport-player`

Instantly move a player to any location.

```bash
curl -X POST http://localhost:8000/api/v1/admin/teleport-player \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "char-hero",
    "destination": {"x": 500, "y": 300, "z": 10},
    "notify_player": true
  }'
```

**Response:**
```json
{
  "success": true,
  "character_id": "char-hero",
  "new_location": {"x": 500, "y": 300, "z": 10}
}
```

---

## Player Management

### Broadcast Message

**Endpoint:** `POST /api/v1/admin/broadcast`

Send a message to all connected players.

```bash
curl -X POST http://localhost:8000/api/v1/admin/broadcast \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Server maintenance in 10 minutes!",
    "message_type": "warning",
    "duration": 10
  }'
```

**Message Types:**
- `announcement` - General announcement (blue)
- `warning` - Warning message (yellow/orange)
- `info` - Information (green)

### Kick Player

**Endpoint:** `POST /api/v1/admin/kick-player`

Remove a player from the session.

```bash
curl -X POST http://localhost:8000/api/v1/admin/kick-player \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 42,
    "reason": "Inappropriate behavior",
    "ban_duration": 60
  }'
```

Parameters:
- `user_id`: User ID to kick
- `reason`: Reason for kick (logged)
- `ban_duration`: Minutes to ban (optional, null = no ban)

---

## Session Management

### List Active Sessions

```bash
curl http://localhost:8000/api/v1/admin/sessions \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Pause/Resume Session

```bash
curl -X POST http://localhost:8000/api/v1/admin/session/game-001/pause \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

curl -X POST http://localhost:8000/api/v1/admin/session/game-001/resume \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### End Session

```bash
curl -X POST http://localhost:8000/api/v1/admin/session/game-001/end \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Real-Time Monitoring

### Admin WebSocket Connection

Connect to WebSocket as admin to monitor all activity:

```javascript
const ws = new WebSocket(
  'ws://localhost:8000/ws/admin-monitor?admin_token=YOUR_ADMIN_TOKEN'
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Game Event:', data);
  
  // Handle different event types
  switch (data.type) {
    case 'player_action':
      console.log(`Player ${data.player_id} performed ${data.action}`);
      break;
    case 'combat_event':
      console.log(`Combat: ${data.attacker} vs ${data.defender}`);
      break;
    case 'player_joined':
      console.log(`Player ${data.player_id} joined session ${data.session_id}`);
      break;
  }
};
```

### Audit Logs

All admin actions are logged with:
- Admin user ID and username
- Action type and timestamp
- Target ID (character, session, etc.)
- Action data and reason
- Session ID (if applicable)

**View Audit Logs:**
```bash
curl http://localhost:8000/api/v1/admin/audit-logs?limit=50 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Admin Actions Reference

### Quick Reference Table

| Action | Endpoint | Method | Description |
|--------|----------|--------|-------------|
| **Monitoring** | | | |
| Server Stats | `/api/v1/admin/stats` | GET | Overall server statistics |
| Session Stats | `/api/v1/admin/session/{id}/stats` | GET | Session-specific stats |
| Audit Logs | `/api/v1/admin/audit-logs` | GET | View admin action history |
| **Entity Management** | | | |
| Spawn Entity | `/api/v1/admin/spawn-entity` | POST | Spawn enemies, NPCs, items |
| Modify Character | `/api/v1/admin/modify-character` | POST | Edit character properties |
| Teleport Player | `/api/v1/admin/teleport-player` | POST | Move player instantly |
| **Communication** | | | |
| Broadcast | `/api/v1/admin/broadcast` | POST | Message all players |
| Kick Player | `/api/v1/admin/kick-player` | POST | Remove player from session |
| **Session Control** | | | |
| List Sessions | `/api/v1/admin/sessions` | GET | View active sessions |
| Pause Session | `/api/v1/admin/session/{id}/pause` | POST | Pause gameplay |
| Resume Session | `/api/v1/admin/session/{id}/resume` | POST | Resume gameplay |
| End Session | `/api/v1/admin/session/{id}/end` | POST | Terminate session |

---

## Web Dashboard Example

### Simple HTML Admin Panel

```html
<!DOCTYPE html>
<html>
<head>
    <title>RPG Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .stat-box { 
            display: inline-block; 
            padding: 20px; 
            margin: 10px; 
            background: #f0f0f0; 
            border-radius: 5px; 
        }
        button { 
            padding: 10px 20px; 
            margin: 5px; 
            cursor: pointer; 
        }
    </style>
</head>
<body>
    <h1>RPG Server Admin</h1>
    
    <div id="stats">
        <h2>Server Statistics</h2>
        <div class="stat-box">
            <h3>Users</h3>
            <p id="total-users">0</p>
        </div>
        <div class="stat-box">
            <h3>Active Sessions</h3>
            <p id="active-sessions">0</p>
        </div>
        <div class="stat-box">
            <h3>Online Players</h3>
            <p id="online-players">0</p>
        </div>
    </div>
    
    <h2>Quick Actions</h2>
    <button onclick="spawnDragon()">Spawn Dragon</button>
    <button onclick="broadcastMessage()">Broadcast Message</button>
    <button onclick="refreshStats()">Refresh Stats</button>
    
    <script>
        const API_URL = 'http://localhost:8000';
        const ADMIN_TOKEN = 'YOUR_ADMIN_JWT_TOKEN'; // Get from login
        
        async function apiCall(endpoint, method = 'GET', body = null) {
            const options = {
                method,
                headers: {
                    'Authorization': `Bearer ${ADMIN_TOKEN}`,
                    'Content-Type': 'application/json'
                }
            };
            if (body) options.body = JSON.stringify(body);
            
            const response = await fetch(`${API_URL}${endpoint}`, options);
            return response.json();
        }
        
        async function refreshStats() {
            const stats = await apiCall('/api/v1/admin/stats');
            document.getElementById('total-users').textContent = stats.total_users;
            document.getElementById('active-sessions').textContent = stats.active_sessions;
            document.getElementById('online-players').textContent = stats.online_players;
        }
        
        async function spawnDragon() {
            const result = await apiCall('/api/v1/admin/spawn-entity', 'POST', {
                session_id: 'game-001',
                entity_type: 'enemy',
                template_id: 'dragon',
                location: {x: 100, y: 200, z: 0},
                quantity: 1
            });
            alert(`Spawned ${result.count} dragon(s)`);
        }
        
        async function broadcastMessage() {
            const message = prompt('Enter message to broadcast:');
            if (message) {
                await apiCall('/api/v1/admin/broadcast', 'POST', {
                    message,
                    message_type: 'announcement',
                    duration: 5
                });
                alert('Message broadcasted!');
            }
        }
        
        // Auto-refresh stats every 10 seconds
        setInterval(refreshStats, 10000);
        refreshStats();
    </script>
</body>
</html>
```

---

## Security Best Practices

### Admin Account Security

1. **Strong Passwords** - Use complex, unique passwords for admin accounts
2. **Regular Rotation** - Change admin passwords regularly
3. **Audit Regularly** - Review audit logs for suspicious activity
4. **Limit Access** - Only give admin role to trusted individuals
5. **Use HTTPS** - Always use HTTPS in production
6. **Rate Limiting** - Implement rate limiting on admin endpoints

### Monitoring

- **Track Admin Actions** - All admin actions are logged
- **Alert on Suspicious Activity** - Set up alerts for unusual patterns
- **Regular Backups** - Backup database regularly before major changes
- **Test in Staging** - Test admin actions in staging environment first

---

## Troubleshooting

### Common Issues

**"Unauthorized" Error:**
- Ensure you're using an admin account (role = "admin")
- Check JWT token is valid and not expired
- Verify Authorization header format

**Entity Not Spawning:**
- Check session_id exists
- Verify location coordinates are valid
- Ensure template_id is correct

**Player Not Receiving Notifications:**
- Verify player is connected via WebSocket
- Check WebSocket connection status
- Ensure notify_player is set to true

---

## Summary

The admin dashboard provides powerful tools for:
- ✅ Real-time game state monitoring
- ✅ In-game entity spawning and editing
- ✅ Player management and moderation
- ✅ Session control and statistics
- ✅ Complete audit trail of all actions

Use these tools responsibly to create engaging experiences and maintain a healthy game environment!

For more information:
- API Documentation: http://localhost:8000/docs
- Client Architecture: CLIENT_ARCHITECTURE.md
- Combat System: REALTIME_COMBAT_GUIDE.md
