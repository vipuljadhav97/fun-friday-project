# 🚀 Quick Start Guide

## Installation (1 minute)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Open in browser
# http://localhost:5000
```

## Creating a Room

1. Click **"✨ Generate New Room"**
2. You get a 6-letter room code (e.g., `ABC123`)
3. Share this code with friends
4. Click **"Enter Room"** to play

## Joining a Room

1. Ask your host for the room code
2. Enter the code (e.g., `ABC123`)
3. Enter your name
4. Click **"🚀 Join Game"**

## Playing

### Step 1: Add Players
- Type a player name in the sidebar
- Click **"+"** to add
- Or bulk add: `Alice, Bob, Charlie` → click **"⚡"**

### Step 2: Create Teams
- Choose team count: 2, 3, 4, or custom
- Click **"🔀 Shuffle & Create Teams"**
- Teams automatically appear and sync to all players

### Step 3: Pick a Game
- **🎡 Wheel of Fortune**: Spin, guess letters, solve puzzles
- **🎤 Antakshari**: Sing Bollywood songs by letter
- **🧩 Guess the Song/Movie**: Emoji puzzles with turns and scoring

## Team Features

- **Shared Across Games**: Same teams used in all games
- **Consistent Members**: Player list synced in real-time
- **Auto Captain**: First player in team is captain (👑)

## Pro Tips

✅ **Real-time Sync**: All changes appear on all players' screens instantly
✅ **Manual Edits**: Add/remove players anytime during setup
✅ **Team Flexing**: Create new teams without restarting
✅ **Solo Play**: Add yourself as a player to set up games
✅ **Mobile Ready**: Play on any device with a browser

## Examples

### 5 Friends Playing Wheel of Fortune

```
1. You create room → Share code ABC123
2. Friends join with their names
3. You add 1 more player (yourself)
4. Create 3 teams (auto-shuffled)
5. Play Wheel of Fortune!
```

### Office Team Event

```
1. Host creates room
2. 20 people join with their names
3. Create 4 teams
4. Play multiple rounds (Wheel → Antakshari → Guess)
5. Teams stay same throughout!
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Room not found" | Check room code (6 letters, uppercase) |
| Players not in sync | Everyone refresh page, rejoin |
| Can't connect | Ensure Flask server is running on port 5000 |
| Room disappeared | Server was restarted; create a new room |

## System Requirements

- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for LAN, use local IP)

## Next Steps

Want to host on your network?
- Get your local IP: `ifconfig | grep inet`
- Start server: `python app.py`
- Share this URL: `http://<YOUR-IP>:5000`
- Friends on same WiFi can join!

---

**Happy gaming! 🎉**
