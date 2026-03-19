# 🎉 Fun Friday - Multiplayer Flask App

A Flask application that enables multiplayer gameplay for the Fun Friday game suite (Wheel of Fortune, Antakshari, and Guess the Song/Movie). Players can create private server rooms and join using room codes.

## Features

- **🎮 Private Game Rooms**: Create rooms with unique 6-letter codes
- **👥 Multi-Player Support**: Invite friends by sharing room code
- **🔄 Real-Time Sync**: WebSocket-based synchronization of player lists and team distribution
- **🎯 Shared Game Logic**: Teams and members stay consistent across all games
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices

## Project Structure

```
fun-friday-multiplayer/
├── app.py                 # Flask server with WebSocket handlers
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── index.html        # Room creation/joining UI
│   └── game.html         # Game wrapper with room info
└── static/
    └── game.html         # The actual game code (Wheel, Antakshari, Guess)
```

## Installation

1. **Clone/Download the project**:
   ```bash
   cd fun-friday-multiplayer
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open in browser**:
   - Navigate to `http://localhost:5000`
   - You'll see the room creation/joining interface

3. **Create or Join a Room**:
   - **Create Room**: Click "Generate New Room" to get a unique room code
   - **Join Room**: Enter a room code and your name, then click "Join Game"

4. **Play the Games**:
   - Add players manually in the sidebar or bulk-add them
   - Create teams using the team distribution controls
   - Select a game (Wheel of Fortune, Antakshari, or Guess the Song/Movie)
   - All connected players see the same teams and game state

## How It Works

### Architecture

- **Backend**: Flask + Flask-SocketIO for real-time bidirectional communication
- **Frontend**: Vanilla JavaScript with WebSocket integration
- **State Management**: Server maintains room state; clients sync via WebSocket
- **Game Logic**: Preserved from the original single-player HTML (no modifications needed)

### Room Management

1. When a room is created, a unique 6-letter code is generated
2. The server stores the room state (players, teams, etc.)
3. Players join using the room code + their name
4. WebSocket events sync:
   - Player list updates (add/remove players)
   - Team count selection
   - Team distribution after shuffle
   - Game state changes

### Player Synchronization

- **Local Actions**: When one player adds/removes a player or creates teams in the sidebar, the action is synced to all players in the room
- **Real-Time Updates**: All connected clients receive updates via Socket.IO events
- **Consistency**: Game logic ensures teams and members remain consistent across different games

## API Endpoints

### HTTP Routes

- `GET /` - Main page (room creation/joining UI)
- `GET /game?code=CODE&name=NAME` - Game page
- `POST /api/room/create` - Create a new room
- `POST /api/room/<code>/join` - Join an existing room
- `GET /api/room/<code>` - Get room state

### WebSocket Events

**Client → Server**:
- `join_game_room` - Join a room with code and player name
- `leave_game_room` - Leave a room
- `update_players` - Sync player list
- `update_team_count` - Update selected team count
- `update_teams` - Sync team distribution
- `get_room_state` - Request current room state

**Server → Client**:
- `player_joined` - Notification when a player joins
- `player_left` - Notification when a player leaves
- `players_updated` - Player list updated
- `team_count_updated` - Team count changed
- `teams_updated` - Team distribution changed
- `room_state` - Current room state snapshot
- `error` - Error message

## Example Usage

1. **Host starts the app**: Opens `http://localhost:5000`
2. **Host creates room**: Clicks "Generate New Room" → Gets code "ABC123"
3. **Host shares code**: Tells friends the code "ABC123"
4. **Friends join**: 
   - Enter room code "ABC123"
   - Enter their name (e.g., "Alice")
   - Click "Join Game"
5. **Host adds players**:
   - Types player names in sidebar
   - Clicks "+", they're added and synced to all players
6. **Host creates teams**:
   - Selects team count (2, 3, 4, or custom)
   - Clicks "Shuffle & Create Teams"
   - Teams are distributed and synced to all players
7. **Play games**:
   - All players see the same teams and captain assignments
   - Game state is shared during gameplay

## Customization

### Adding More Games

- Add game definitions to the `gameData` object in `/static/game.html`
- Create new game logic functions following the pattern of existing games
- No backend changes needed for the server to support new games

### Modifying Room Size Limits

Edit `app.py`:
- Max players per room: Modify `bulkAddPlayers()` in game.html (currently 200)
- Max rooms: No hard limit; in-memory storage

### Changing Port

Edit `app.py` last line:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=8000)  # Change 5000 to 8000
```

## Troubleshooting

### "Connection failed" message
- Ensure Flask server is running
- Check if port 5000 is in use: `lsof -i :5000`
- Try a different port in `app.py`

### Players not seeing team updates
- Ensure all players are in the same room (same code)
- Check browser console for WebSocket errors
- Refresh the page and rejoin

### Room code not working
- Ensure code entered is exactly 6 characters (uppercase)
- Code is case-insensitive (converted to uppercase internally)

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Performance Notes

- Server stores rooms in-memory (RAM)
- Rooms persist until all players leave
- No database persistence (data lost on server restart)
- For production, consider adding Redis or database persistence

## Future Enhancements

- [ ] Database persistence (store rooms to database)
- [ ] Spectator mode (watch without playing)
- [ ] Game recordings and statistics
- [ ] Chat in the room
- [ ] Admin controls for room host
- [ ] AI players for solo practice
- [ ] Mobile app version

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions, check:
1. Browser console for JavaScript errors
2. Terminal for Flask server logs
3. `/api/room/<code>` endpoint to inspect room state

---

**Made with ❤️ for Fun Friday Game Nights!** 🎉
