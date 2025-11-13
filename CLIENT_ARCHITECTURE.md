# Client Architecture Blueprint

Complete blueprint for building cross-platform RPG clients that connect to the server-authoritative backend.

## Architecture Overview

The system follows a **server-authoritative** architecture where:
- **Server**: Has final authority on all game state and calculations
- **Client**: Displays state and submits action requests only

```
CLIENT                                SERVER
┌────────────────┐                  ┌────────────────┐
│   UI/Renderer  │                  │  Game Engine   │
│   ↓            │                  │   ↓            │
│   Input        │  ──Actions──→    │  Validation    │
│   ↓            │                  │   ↓            │
│   Prediction   │  ←──Updates──    │  Calculation   │
│   (Optional)   │                  │   ↓            │
│   ↓            │                  │  Broadcast     │
│   Display      │  ←─WebSocket─    │   State        │
└────────────────┘                  └────────────────┘
```

## Key Principles

1. **Server Authority** - Server decides all outcomes
2. **Action Submission** - Clients submit requests, not results
3. **Client Prediction** - Predict for smooth UX (optional)
4. **Server Reconciliation** - Correct predictions with server truth

## What Clients Do vs Don't Do

### ✅ Client Responsibilities

- Render game world from server state
- Capture and queue user input
- Submit action requests to server
- Receive and display server updates
- (Optional) Predict outcomes for smooth UX
- Cache static assets
- Handle UI/UX

### ❌ Client NEVER Does

- Calculate damage or game outcomes
- Generate loot or XP
- Make authoritative state changes
- Store encryption keys
- Validate actions (server does this)

## Communication Patterns

### 1. REST API (Actions)

```javascript
// Submit action request
async function attackEnemy(characterId, enemyId) {
    const response = await fetch('/api/v1/combat/attack', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${jwt}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            attacker_id: characterId,
            defender_id: enemyId,
            session_id: currentSession
        })
    });
    
    return await response.json();  // Server calculates damage
}
```

### 2. WebSocket (Real-Time)

```javascript
const ws = new WebSocket('ws://server/ws/player123');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    
    switch (update.type) {
        case 'player_moved':
            updatePosition(update.player_id, update.location);
            break;
        case 'combat_event':
            displayDamage(update);
            break;
        case 'chat_message':
            showMessage(update);
            break;
    }
};
```

## Platform Implementations

### Web (JavaScript)

**Tech Stack:**
- Framework: React/Vue/vanilla JS
- 3D: Three.js, Babylon.js
- 2D: Phaser, PixiJS
- State: Redux, Zustand

**Example:**
```javascript
class GameClient {
    constructor(serverUrl, jwtToken) {
        this.serverUrl = serverUrl;
        this.token = jwtToken;
        this.ws = null;
        this.state = {};
    }
    
    async connect() {
        this.ws = new WebSocket(`${this.serverUrl}/ws/player`);
        this.ws.onmessage = (e) => this.handleUpdate(JSON.parse(e.data));
    }
    
    async submitAction(action) {
        const response = await fetch(`${this.serverUrl}/api/v1/actions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(action)
        });
        return response.json();
    }
    
    handleUpdate(update) {
        // Update local state for rendering
        this.state = {...this.state, ...update};
        this.render();
    }
}
```

### Unity (C#)

```csharp
using UnityEngine;
using WebSocketSharp;
using Newtonsoft.Json;

public class GameClient : MonoBehaviour
{
    private WebSocket ws;
    private string jwtToken;
    
    void Start()
    {
        ConnectToServer();
    }
    
    void ConnectToServer()
    {
        ws = new WebSocket("ws://server/ws/unity-client");
        ws.OnMessage += HandleServerUpdate;
        ws.Connect();
    }
    
    void HandleServerUpdate(object sender, MessageEventArgs e)
    {
        var update = JsonConvert.DeserializeObject<ServerUpdate>(e.Data);
        
        switch (update.type)
        {
            case "player_moved":
                UpdatePlayerPosition(update);
                break;
            case "combat_event":
                DisplayCombatEffect(update);
                break;
        }
    }
    
    public async void SubmitAction(string actionType, object data)
    {
        var action = new { type = actionType, data = data };
        ws.Send(JsonConvert.SerializeObject(action));
    }
}
```

### Mobile (React Native)

```typescript
import { WebSocket } from 'react-native';

class MobileGameClient {
    private ws: WebSocket;
    
    constructor(serverUrl: string, token: string) {
        this.ws = new WebSocket(serverUrl);
        
        this.ws.onopen = () => {
            this.authenticate(token);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleUpdate(data);
        };
    }
    
    authenticate(token: string) {
        this.ws.send(JSON.stringify({
            type: 'auth',
            token: token
        }));
    }
    
    submitAction(action: any) {
        this.ws.send(JSON.stringify(action));
    }
    
    handleUpdate(update: any) {
        // Update React state for rendering
    }
}
```

## State Management

### Local Caching

```javascript
const localCache = {
    characters: {},
    enemies: {},
    items: {},
    npcs: {}
};

function updateCache(update) {
    const { entityType, entityId, data } = update;
    localCache[entityType][entityId] = {
        ...localCache[entityType][entityId],
        ...data,
        lastUpdate: Date.now()
    };
}
```

### Client Prediction (Optional)

```javascript
class Predictor {
    predictions = new Map();
    sequence = 0;
    
    predictMove(charId, destination) {
        const seq = this.sequence++;
        this.predictions.set(seq, {
            charId,
            oldLoc: localCache.characters[charId].location,
            newLoc: destination
        });
        
        // Apply prediction immediately
        localCache.characters[charId].location = destination;
        return seq;
    }
    
    reconcile(serverUpdate) {
        // Remove confirmed predictions
        this.predictions.forEach((pred, seq) => {
            if (seq <= serverUpdate.sequence) {
                this.predictions.delete(seq);
            }
        });
        
        // Update with server truth
        localCache.characters[serverUpdate.charId].location = 
            serverUpdate.location;
        
        // Reapply unconfirmed predictions
        this.predictions.forEach(pred => {
            if (pred.charId === serverUpdate.charId) {
                localCache.characters[pred.charId].location = pred.newLoc;
            }
        });
    }
}
```

## Security Best Practices

### JWT Token Management

```javascript
class TokenManager {
    constructor() {
        this.token = null;
    }
    
    async login(username, password) {
        const response = await fetch('/api/v1/users/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        this.token = data.access_token;
        this.secureStore('token', this.token);
    }
    
    getAuthHeader() {
        return `Bearer ${this.token}`;
    }
    
    secureStore(key, value) {
        // Use platform-specific secure storage
        // NOT localStorage in production!
    }
}
```

## Performance Optimization

### Object Pooling

```javascript
class ObjectPool {
    constructor(createFn, size = 10) {
        this.pool = Array(size).fill(null).map(() => createFn());
    }
    
    acquire() {
        return this.pool.pop() || this.createFn();
    }
    
    release(obj) {
        obj.reset();
        this.pool.push(obj);
    }
}
```

### Batching Updates

```javascript
const updateQueue = [];

function queueUpdate(update) {
    updateQueue.push(update);
}

setInterval(() => {
    if (updateQueue.length > 0) {
        applyBatchedUpdates(updateQueue);
        updateQueue.length = 0;
    }
}, 100);  // Batch every 100ms
```

## Error Handling

```javascript
class ErrorHandler {
    async handleConnectionError() {
        console.error('Connection lost');
        await this.reconnect();
    }
    
    async reconnect() {
        let attempts = 0;
        while (attempts < 5) {
            try {
                await this.connect();
                return;
            } catch (err) {
                attempts++;
                await this.delay(2000 * attempts);
            }
        }
        throw new Error('Could not reconnect');
    }
}
```

## Cross-Platform Checklist

### Must Have (All Platforms):
- [ ] JWT authentication
- [ ] WebSocket connection
- [ ] REST API client
- [ ] Local state cache
- [ ] Error handling
- [ ] Reconnection logic
- [ ] Secure token storage

### Platform-Specific:
- **Web**: Browser compatibility, PWA support
- **Unity**: Native plugins, addressables
- **Mobile**: Background handling, push notifications

## Summary

The client architecture emphasizes:

1. **Server Authority** - Server decides everything
2. **Simple Clients** - Just display and submit actions
3. **Security** - No game logic on client
4. **Performance** - Smart caching and prediction
5. **Cross-Platform** - Same principles apply everywhere

For more info:
- Admin Guide: ADMIN_DASHBOARD_GUIDE.md
- API Docs: http://localhost:8000/docs
- Combat: REALTIME_COMBAT_GUIDE.md
