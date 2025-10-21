# Bastards Blood RPG API Examples

This directory contains example scripts demonstrating how to use the Bastards Blood RPG API.

## Prerequisites

1. Install Python dependencies:
   ```bash
   pip install requests
   ```

2. Start the API server:
   ```bash
   cd /home/runner/work/bastards-blood/bastards-blood
   python run_server.py
   ```

## Examples

### basic_usage.py

Demonstrates the basic workflow of:
- Creating a game session
- Creating a character
- Performing actions (attacks, damage, healing)
- Recording player speech
- Getting game state

**Run it:**
```bash
python examples/basic_usage.py
```

## Expected Output

The example script will:
1. ✓ Check API health
2. ✓ Create a new session
3. ✓ Create a character
4. ✓ Add character to session
5. ✓ Record speech
6. ✓ Perform attack action
7. ✓ Apply damage
8. ✓ Apply healing
9. ✓ Show final game state

All actions are recorded as events in the session log and can be replayed or analyzed later.
