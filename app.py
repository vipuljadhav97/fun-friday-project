from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets
import string
import json
import threading
import random
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for rooms and players
rooms = {}
# Track which room each socket is in: {sid: {'room_code': ..., 'is_host': ...}}
sid_room_map = {}
# Grace period timers for disconnects: {(room_code, player_name): {'timer': Timer, 'player_data': {...}}}
disconnect_timers = {}

WOF_PUZZLES = [
    {'category': 'Bollywood', 'phrase': 'DILWALE DULHANIA LE JAYENGE'},
    {'category': 'Bollywood', 'phrase': 'SHOLAY'},
    {'category': 'Bollywood', 'phrase': 'THREE IDIOTS'},
    {'category': 'Bollywood', 'phrase': 'KABHI KHUSHI KABHIE GHAM'},
    {'category': 'Bollywood', 'phrase': 'DANGAL'},
    {'category': 'Bollywood', 'phrase': 'BAJRANGI BHAIJAAN'},
    {'category': 'Bollywood', 'phrase': 'ZINDAGI NA MILEGI DOBARA'},
    {'category': 'Bollywood', 'phrase': 'QUEEN'},
    {'category': 'Bollywood', 'phrase': 'ANDAZ APNA APNA'},
    {'category': 'Bollywood', 'phrase': 'DIL CHAHTA HAI'},
    {'category': 'Bollywood', 'phrase': 'LAGAAN'},
    {'category': 'Bollywood', 'phrase': 'MUGHAL E AZAM'},
    {'category': 'Hollywood', 'phrase': 'THE DARK KNIGHT'},
    {'category': 'Hollywood', 'phrase': 'INCEPTION'},
    {'category': 'Hollywood', 'phrase': 'TITANIC'},
    {'category': 'Hollywood', 'phrase': 'AVENGERS ENDGAME'},
    {'category': 'Hollywood', 'phrase': 'THE LION KING'},
    {'category': 'Hollywood', 'phrase': 'JURASSIC PARK'},
    {'category': 'Indian Landmarks', 'phrase': 'TAJ MAHAL AGRA'},
    {'category': 'Indian Landmarks', 'phrase': 'GATEWAY OF INDIA MUMBAI'},
    {'category': 'Indian Landmarks', 'phrase': 'RED FORT DELHI'},
    {'category': 'Indian Landmarks', 'phrase': 'HAWA MAHAL JAIPUR'},
    {'category': 'Indian Landmarks', 'phrase': 'GOLDEN TEMPLE AMRITSAR'},
    {'category': 'Desi Food', 'phrase': 'BUTTER CHICKEN'},
    {'category': 'Desi Food', 'phrase': 'PANI PURI'},
    {'category': 'Desi Food', 'phrase': 'MASALA DOSA'},
    {'category': 'Desi Food', 'phrase': 'BIRYANI'},
    {'category': 'Desi Food', 'phrase': 'CHOLE BHATURE'},
    {'category': 'Indian Festivals', 'phrase': 'DIWALI FESTIVAL OF LIGHTS'},
    {'category': 'Indian Festivals', 'phrase': 'HOLI FESTIVAL OF COLORS'},
    {'category': 'Indian Festivals', 'phrase': 'GANESH CHATURTHI'},
    {'category': 'Indian Festivals', 'phrase': 'DURGA PUJA'},
    {'category': 'Famous Personalities', 'phrase': 'MAHATMA GANDHI'},
    {'category': 'Famous Personalities', 'phrase': 'SACHIN TENDULKAR'},
    {'category': 'Famous Personalities', 'phrase': 'APJ ABDUL KALAM'},
    {'category': 'Famous Personalities', 'phrase': 'AMITABH BACHCHAN'},
    {'category': 'Famous Personalities', 'phrase': 'LATA MANGESHKAR'},
    {'category': 'Famous Personalities', 'phrase': 'VIRAT KOHLI'},
    {'category': 'Hindi Phrases', 'phrase': 'ATITHI DEVO BHAVA'},
    {'category': 'Hindi Phrases', 'phrase': 'SATYAMEV JAYATE'},
    {'category': 'Hindi Phrases', 'phrase': 'VASUDHAIVA KUTUMBAKAM'},
    {'category': 'English Phrases', 'phrase': 'UNITY IN DIVERSITY'},
    {'category': 'English Phrases', 'phrase': 'INCREDIBLE INDIA'},
    {'category': 'English Phrases', 'phrase': 'KNOWLEDGE IS POWER'},
    {'category': 'English Phrases', 'phrase': 'THE SHOW MUST GO ON'},
]

EMOJI_MOVIE_PUZZLES = [
    {'emoji': '🦁👑🌍', 'answer': 'The Lion King', 'hint': 'Animated Disney classic set in the Pride Lands'},
    {'emoji': '🕐🚗⚡👴👦', 'answer': 'Back to the Future', 'hint': 'A time-traveling DeLorean and Doc Brown'},
    {'emoji': '🚢💎🧊', 'answer': 'Titanic', 'hint': 'Ship, iceberg, and "My Heart Will Go On"'},
    {'emoji': '🦖🏞️⚠️', 'answer': 'Jurassic Park', 'hint': 'Dinosaurs in a theme park gone wrong'},
    {'emoji': '🦇🌃🃏', 'answer': 'The Dark Knight', 'hint': 'Batman faces the Joker in Gotham'},
    {'emoji': '💤🧠🏙️', 'answer': 'Inception', 'hint': 'Dream within a dream heist'},
    {'emoji': '🙎🏻‍♂️🟩💊🕶️', 'answer': 'The Matrix', 'hint': 'Choose the red or blue pill'},
    {'emoji': '🐟🔍🌊', 'answer': 'Finding Nemo', 'hint': 'A father searches the ocean for his son'},
    {'emoji': '🦍🏙️🗽', 'answer': 'King Kong', 'hint': 'Giant ape climbs a famous skyscraper'},
    {'emoji': '🏠👦🎄', 'answer': 'Home Alone', 'hint': 'Kid protects his house from burglars'},
    {'emoji': '🧸🧑‍🚀🤠🚀', 'answer': 'Toy Story', 'hint': 'Woody and Buzz adventure'},
    {'emoji': '❄️👭⛄', 'answer': 'Frozen', 'hint': 'Sisters, ice powers, and "Let It Go"'},
    {'emoji': '🧑‍🚀🌌🪐', 'answer': 'Interstellar', 'hint': 'Space mission to save humanity'},
    {'emoji': '🕵️‍♂️❌💣🛩️', 'answer': 'Mission Impossible', 'hint': 'Ethan Hunt action franchise'},
    {'emoji': '💰❓👦🏽', 'answer': 'Slumdog Millionaire', 'hint': 'Game show and destiny in Mumbai'},
    {'emoji': '✈️🏍️🕶️🔥', 'answer': 'Top Gun', 'hint': 'Fighter pilot Maverick'},
    {'emoji': '🚗💨👨‍👨‍👧', 'answer': 'Fast and Furious', 'hint': 'Street racing and family theme'},
    {'emoji': '🧙‍♂️🌀⏳', 'answer': 'Doctor Strange', 'hint': 'Marvel sorcerer and multiverse portals'},
    {'emoji': '🐆👑🛡️', 'answer': 'Black Panther', 'hint': 'Wakanda forever'},
    {'emoji': '🤖❤️🦾', 'answer': 'Iron Man', 'hint': 'Tony Stark builds a powered suit'},
    {'emoji': '📱💻👥', 'answer': 'The Social Network', 'hint': 'Origin story of a famous social media platform'},
    {'emoji': '🎹💃🌃', 'answer': 'La La Land', 'hint': 'Musical romance in Los Angeles'},
    {'emoji': '🧑‍🦽‍➡️🔵🌳🧑', 'answer': 'Avatar', 'hint': 'Pandora and the Navi'},
    {'emoji': '🤠🧑‍🦯🫟🔫🔥', 'answer': 'Sholay', 'hint': 'Classic Bollywood action drama with Jai and Veeru'},
    {'emoji': '❤️🚆🐦🌾', 'answer': 'Dilwale Dulhania Le Jayenge', 'hint': 'Raj and Simran iconic romance'},
    {'emoji': '3️⃣🤪🎓', 'answer': '3 Idiots', 'hint': 'Engineering college story of three friends'},
    {'emoji': '🏏💰🇮🇳', 'answer': 'Lagaan', 'hint': 'Villagers challenge the British in a cricket match'},
    {'emoji': '🤼‍♀️👨‍👧‍👧🏅', 'answer': 'Dangal', 'hint': 'Wrestling journey of a father and daughters'},
    {'emoji': '🚗🍅🛣️🌊', 'answer': 'Zindagi Na Milegi Dobara', 'hint': 'Road trip film about friendship and life'},
    {'emoji': '👬😂💰', 'answer': 'Andaz Apna Apna', 'hint': 'Cult comedy with Amar and Prem'},
]

EMOJI_SONG_PUZZLES = [
    {'emoji': '🔺❤️🫵', 'answer': 'Shape of You', 'hint': 'Ed Sheeran global hit'},
    {'emoji': '🙏💭', 'answer': 'Believer', 'hint': 'Imagine Dragons anthem'},
    {'emoji': '👋🚗🌅', 'answer': 'See You Again', 'hint': 'Tribute song from Fast and Furious 7'},
    {'emoji': '💍❤️👌', 'answer': 'Perfect', 'hint': 'Romantic ballad by Ed Sheeran'},
    {'emoji': '👑🪨🫵', 'answer': 'We Will Rock You', 'hint': 'Stomp-stomp-clap stadium chant'},
    {'emoji': '🚂🌉💃', 'answer': 'Chaiyya Chaiyya', 'hint': 'Bollywood song shot on a moving train'},
    {'emoji': '🫵❤️🌧️', 'answer': 'Tum Hi Ho', 'hint': 'Aashiqui 2 superhit romantic song'},
    {'emoji': '📅✅❌✅', 'answer': 'Kal Ho Naa Ho', 'hint': 'Title track from Shah Rukh Khan film'},
    {'emoji': '🇮🇳🙌', 'answer': 'Jai Ho', 'hint': 'Oscar-winning song from Slumdog Millionaire'},
    {'emoji': '💃🕺☀️', 'answer': 'Senorita', 'hint': 'Popular dance track from ZNMD'},
    {'emoji': '🐯🕺🕺🔥', 'answer': 'Naatu Naatu', 'hint': 'High-energy dance song from RRR'},
    {'emoji': '🛳️✊🗣️🎉👫💍', 'answer': 'Gallan Goodiyaan', 'hint': 'Party song from Dil Dhadakne Do'},
    {'emoji': '👦⏰✅', 'answer': 'Apna Time Aayega', 'hint': 'Motivational rap from Gully Boy'},
]


def _normalize_used_ids(raw_ids):
    used_ids = set()
    for value in raw_ids or []:
        try:
            used_ids.add(int(value))
        except (TypeError, ValueError):
            continue
    return used_ids

def generate_room_code(length=6):
    """Generate a random 6-character room code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def get_or_create_room(room_code):
    """Get a room or create it if it doesn't exist."""
    if room_code not in rooms:
        rooms[room_code] = {
            'code': room_code,
            'created_at': datetime.now().isoformat(),
            'players': {},  # {player_id: {name, joined_at}}
            'current_teams': [],
            'selected_team_count': 2,
            'current_team_points': {},
            'current_players_list': []  # ordered list for frontend
        }
    return rooms[room_code]

@app.route('/')
def index():
    """Home page - show room creation/joining UI."""
    return render_template('index.html')

@app.route('/game')
def game():
    """Game page - show game with room sync."""
    room_code = request.args.get('code', '').upper()
    player_name = request.args.get('name', '')
    
    if not room_code or not player_name:
        return '<script>window.location.href="/";</script>'
    
    return render_template('game.html')

@app.route('/api/room/create', methods=['POST'])
def create_room():
    """Create a new room and return the code."""
    data = request.get_json() or {}
    host_name = data.get('host_name', '').strip()
    
    room_code = generate_room_code()
    room = get_or_create_room(room_code)
    room['host_name'] = host_name
    return jsonify({'success': True, 'room_code': room_code})

@app.route('/api/room/<room_code>/join', methods=['POST'])
def join_room_endpoint(room_code):
    """Validate and join a room."""
    room_code = room_code.upper()
    data = request.get_json() or {}
    player_name = data.get('player_name', '').strip()
    
    if not player_name:
        return jsonify({'success': False, 'error': 'Player name required'}), 400
    
    room_code = room_code.upper()
    if room_code not in rooms:
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    return jsonify({'success': True, 'room_code': room_code})

@app.route('/api/room/<room_code>')
def get_room_state(room_code):
    """Get current room state (players, teams, etc)."""
    room_code = room_code.upper()
    if room_code not in rooms:
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    room = rooms[room_code]
    return jsonify({
        'success': True,
        'room': {
            'code': room['code'],
            'players': room['current_players_list'],
            'teams': room['current_teams'],
            'team_count': room['selected_team_count'],
            'team_points': room.get('current_team_points', {})
        }
    })


@app.route('/api/puzzle/wof/random', methods=['POST'])
def get_wof_puzzle():
    """Return one Wheel of Fortune puzzle from the server-side bank."""
    data = request.get_json(silent=True) or {}
    used_ids = _normalize_used_ids(data.get('used_ids', []))

    available = [(idx, puzzle) for idx, puzzle in enumerate(WOF_PUZZLES) if idx not in used_ids]
    if not available:
        available = list(enumerate(WOF_PUZZLES))

    if not available:
        return jsonify({'success': False, 'error': 'No puzzles configured'}), 500

    puzzle_id, puzzle = random.choice(available)
    return jsonify({
        'success': True,
        'puzzle': {
            'id': puzzle_id,
            'category': puzzle['category'],
            'phrase': puzzle['phrase']
        }
    })


@app.route('/api/puzzle/emoji/questions', methods=['POST'])
def get_emoji_questions():
    """Return a randomized set of emoji questions from server-side banks."""
    data = request.get_json(silent=True) or {}
    mode = str(data.get('mode', 'mixed')).strip().lower()

    try:
        count = int(data.get('count', 10))
    except (TypeError, ValueError):
        count = 10

    count = max(1, min(count, 60))

    movie_pool = [
        {'emoji': q['emoji'], 'answer': q['answer'], 'hint': q['hint'], 'category': 'Movie'}
        for q in EMOJI_MOVIE_PUZZLES
    ]
    song_pool = [
        {'emoji': q['emoji'], 'answer': q['answer'], 'hint': q['hint'], 'category': 'Song'}
        for q in EMOJI_SONG_PUZZLES
    ]

    if mode == 'movies':
        pool = movie_pool
    elif mode == 'songs':
        pool = song_pool
    else:
        pool = movie_pool + song_pool

    if count > len(pool):
        return jsonify({'success': False, 'error': 'Not enough puzzles available'}), 400

    return jsonify({'success': True, 'questions': random.sample(pool, count)})

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Player connects to WebSocket."""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Player disconnects — start grace period before cleanup."""
    player_id = request.sid
    print(f"Client disconnected: {player_id}")
    
    mapping = sid_room_map.pop(player_id, None)
    if not mapping:
        return
    
    room_code = mapping['room_code']
    if room_code not in rooms:
        return
    
    room = rooms[room_code]
    if player_id not in room['players']:
        return
    
    leaving_player = room['players'][player_id]
    player_name = leaving_player['name']
    is_host = leaving_player.get('is_host', False)
    
    # Remove the old sid entry (stale socket)
    del room['players'][player_id]
    leave_room(room_code, sid=player_id)
    
    # Start a grace period — if they reconnect within 10s, no cleanup happens
    timer_key = (room_code, player_name)
    
    def do_cleanup():
        """Runs after grace period if the player didn't reconnect."""
        disconnect_timers.pop(timer_key, None)
        if room_code not in rooms:
            return
        room = rooms[room_code]
        if is_host:
            socketio.emit('room_closed', {
                'message': 'Host has left. Room is closed.'
            }, room=room_code)
            for pid in list(room['players'].keys()):
                sid_room_map.pop(pid, None)
                leave_room(room_code, sid=pid)
            rooms.pop(room_code, None)
        else:
            room['current_players_list'] = [
                p for p in room['players'].values() if not p.get('is_host')
            ]
            socketio.emit('player_left', {
                'player_id': player_id,
                'player_name': player_name,
                'players': room['current_players_list']
            }, room=room_code)
            if len(room['players']) == 0:
                rooms.pop(room_code, None)
    
    # Cancel any existing timer for this player (e.g. rapid reconnects)
    existing = disconnect_timers.pop(timer_key, None)
    if existing:
        existing['timer'].cancel()
    
    timer = threading.Timer(10.0, do_cleanup)
    disconnect_timers[timer_key] = {'timer': timer, 'player_data': leaving_player}
    timer.start()
    print(f"Grace period started for {player_name} in room {room_code}")

@socketio.on('join_game_room')
def handle_join_game_room(data):
    """Player joins a game room via WebSocket."""
    room_code = data.get('room_code', '').upper()
    player_name = data.get('player_name', '').strip()
    is_host = data.get('is_host', False)
    player_id = request.sid
    
    if not room_code or not player_name:
        emit('error', {'message': 'Invalid room code or player name'})
        return
    
    room = get_or_create_room(room_code)
    
    # Cancel any pending disconnect timer for this player (reconnect/refresh)
    timer_key = (room_code, player_name)
    existing_timer = disconnect_timers.pop(timer_key, None)
    if existing_timer:
        existing_timer['timer'].cancel()
        print(f"Reconnect: cancelled disconnect timer for {player_name} in room {room_code}")
    
    # Remove any stale entries for the same player name (handles reconnect race)
    stale_sids = [
        sid for sid, p in room['players'].items()
        if p['name'].lower() == player_name.lower() and sid != player_id
    ]
    for sid in stale_sids:
        del room['players'][sid]
        sid_room_map.pop(sid, None)
    
    # Track connection in room (host or player)
    room['players'][player_id] = {
        'id': player_id,
        'name': player_name,
        'is_host': is_host,
        'joined_at': datetime.now().isoformat()
    }
    
    # Track sid -> room mapping for disconnect cleanup
    sid_room_map[player_id] = {'room_code': room_code, 'is_host': is_host}
    
    # Only non-host connections count as players
    room['current_players_list'] = [
        p for p in room['players'].values() if not p.get('is_host')
    ]
    
    # Join Socket.IO room
    join_room(room_code)
    
    # Notify all in the room
    emit('player_joined', {
        'player_id': player_id,
        'player_name': player_name,
        'is_host': is_host,
        'players': room['current_players_list']
    }, room=room_code)
    
    # Send full room state to the joining/reconnecting client
    emit('room_state', {
        'code': room_code,
        'players': room['current_players_list'],
        'teams': room.get('current_teams', []),
        'team_count': room.get('selected_team_count', 2),
        'team_points': room.get('current_team_points', {})
    })

@socketio.on('leave_game_room')
def handle_leave_game_room(data):
    """Player leaves a game room."""
    room_code = data.get('room_code', '').upper()
    player_id = request.sid
    
    if room_code in rooms:
        room = rooms[room_code]
        if player_id in room['players']:
            leaving_player = room['players'][player_id]
            player_name = leaving_player['name']
            is_host = leaving_player.get('is_host', False)
            
            # Remove from sid tracking
            sid_room_map.pop(player_id, None)
            
            if is_host:
                # Host is leaving — close the entire room
                emit('room_closed', {
                    'message': 'Host has left. Room is closed.'
                }, room=room_code)
                # Remove all players from the Socket.IO room
                for pid in list(room['players'].keys()):
                    sid_room_map.pop(pid, None)
                    leave_room(room_code, sid=pid)
                del rooms[room_code]
            else:
                del room['players'][player_id]
                room['current_players_list'] = [
                    p for p in room['players'].values() if not p.get('is_host')
                ]
                
                leave_room(room_code)
                
                # Notify remaining players
                emit('player_left', {
                    'player_id': player_id,
                    'player_name': player_name,
                    'players': room['current_players_list']
                }, room=room_code)
                
                # Delete room if empty
                if len(room['players']) == 0:
                    del rooms[room_code]

@socketio.on('update_players')
def handle_update_players(data):
    """Update players list (manual add/remove)."""
    room_code = data.get('room_code', '').upper()
    players_data = data.get('players', [])
    
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = rooms[room_code]
    # Store players as dictionaries for backend
    room['current_players_list'] = players_data
    
    # Broadcast to all clients in the room
    emit('players_updated', {
        'players': players_data,
        'count': len(players_data)
    }, room=room_code)

@socketio.on('update_team_count')
def handle_update_team_count(data):
    """Update selected team count."""
    room_code = data.get('room_code', '').upper()
    team_count = data.get('team_count', 2)
    
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = rooms[room_code]
    room['selected_team_count'] = team_count
    
    emit('team_count_updated', {
        'team_count': team_count
    }, room=room_code)

@socketio.on('update_teams')
def handle_update_teams(data):
    """Update team distribution."""
    room_code = data.get('room_code', '').upper()
    teams = data.get('teams', [])
    
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = rooms[room_code]
    room['current_teams'] = teams
    
    emit('teams_updated', {
        'teams': teams
    }, room=room_code)

@socketio.on('update_team_points')
def handle_update_team_points(data):
    """Update accumulated team points."""
    room_code = data.get('room_code', '').upper()
    team_points = data.get('team_points', {})

    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return

    room = rooms[room_code]
    room['current_team_points'] = team_points

    emit('team_points_updated', {
        'team_points': team_points
    }, room=room_code)

@socketio.on('host_message')
def handle_host_message(data):
    """Host sends a private message to a specific player."""
    room_code = data.get('room_code', '').upper()
    target_player_name = data.get('target_name', '').strip()
    message = data.get('message', '').strip()
    sender_id = request.sid
    
    if not message or not target_player_name:
        return
    
    if room_code not in rooms:
        return
    
    room = rooms[room_code]
    
    # Verify sender is the host
    sender = room['players'].get(sender_id)
    if not sender or not sender.get('is_host'):
        return
    
    # Find target player's socket ID by name
    target_sid = None
    for pid, pdata in room['players'].items():
        if pdata['name'].lower() == target_player_name.lower() and not pdata.get('is_host'):
            target_sid = pid
            break
    
    if target_sid:
        emit('host_message', {
            'from': 'Host',
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M')
        }, room=target_sid)

@socketio.on('player_reply')
def handle_player_reply(data):
    """Player sends a reply to the host."""
    room_code = data.get('room_code', '').upper()
    message = data.get('message', '').strip()
    sender_id = request.sid
    
    if not message:
        return
    
    if room_code not in rooms:
        return
    
    room = rooms[room_code]
    
    # Verify sender is a non-host player
    sender = room['players'].get(sender_id)
    if not sender or sender.get('is_host'):
        return
    
    # Find host's socket ID
    host_sid = None
    for pid, pdata in room['players'].items():
        if pdata.get('is_host'):
            host_sid = pid
            break
    
    if host_sid:
        emit('player_reply', {
            'from': sender['name'],
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M')
        }, room=host_sid)

@socketio.on('get_room_state')
def handle_get_room_state(data):
    """Get current room state."""
    room_code = data.get('room_code', '').upper()
    
    if room_code not in rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = rooms[room_code]
    emit('room_state', {
        'code': room_code,
        'players': room['current_players_list'],
        'teams': room['current_teams'],
        'team_count': room['selected_team_count'],
        'team_points': room.get('current_team_points', {})
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
