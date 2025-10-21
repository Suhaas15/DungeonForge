from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import json
from elevenlabs import ElevenLabs, VoiceSettings, DialogueInput
import io
import re
import threading

# Load .env from parent directory (root of project)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)

# CORS configuration - allow frontend URL from environment or localhost
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
CORS(app, resources={r"/*": {"origins": [FRONTEND_URL, "http://localhost:3000"]}})

# Initialize Airia configuration
AIRIA_API_KEY = os.getenv('AIRIA_API_KEY')
AIRIA_USER_ID = os.getenv('AIRIA_USER_ID', str(uuid.uuid4()))
AIRIA_PIPELINE_URL = "https://api.airia.ai/v2/PipelineExecution/74d3e775-1b60-42f2-be75-e3fb963a5e02"

# Initialize ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
elevenlabs_client = None
if ELEVENLABS_API_KEY:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Stack-AI Image Generation Configuration
STACK_AI_API_URL = os.getenv('STACK_AI_API_URL')
STACK_AI_API_KEY = os.getenv('STACK_AI_API_KEY')

# Voice IDs for different characters/roles
VOICE_ROLES = {
    'narrator': 'JBFqnCBsd6RMkjVDRZzb',  # George - British narrator
    'character1': 'EXAVITQu4vr4xnSDxMaL',  # Sarah - Female character
    'character2': 'onwK4e9ZLuTAKqWW03F9',  # Daniel - Male character
    'character3': 'TX3LPaxmHKxFdv7VOQHJ',  # Rachel - Female character
    'monster': '21m00Tcm4TlvDq8ikWAM',  # Josh - Deep male voice for monsters
}

# Lobby management
lobbies = {}  # {lobby_id: lobby_data}
user_sessions = {}  # {user_id: lobby_id}
starting_lobbies = set()  # Track lobbies currently starting

# Image generation cache
image_cache = {}  # {request_id: image_url}

def call_airia_agent(user_input):
    """Call Airia agent and return the response"""
    try:
        payload = json.dumps({
            "userId": AIRIA_USER_ID,
            "request": user_input,
            "asyncOutput": False
        })
        
        headers = {
            "X-API-KEY": AIRIA_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(AIRIA_PIPELINE_URL, headers=headers, data=payload, timeout=90)
        
        if response.status_code == 200:
            response_data = response.json()
            # Extract the actual text response from Airia's response structure
            # Adjust this based on the actual response format from your agent
            if isinstance(response_data, dict):
                # Try common response fields
                return response_data.get('output') or response_data.get('result') or response_data.get('response') or str(response_data)
            return str(response_data)
        else:
            print(f"Airia API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error calling Airia agent: {e}")
        return None

def generate_scene_image_async(summary_text, user_id, result_dict, key):
    """Generate scene image in background thread"""
    try:
        image_url = generate_scene_image(summary_text, user_id)
        result_dict[key] = image_url
    except Exception as e:
        print(f"[Stack-AI] Background image generation failed: {e}")
        result_dict[key] = None

def generate_scene_image(summary_text, user_id="default"):
    """Call Stack-AI image generation API with the scene summary"""
    try:
        if not STACK_AI_API_URL or not STACK_AI_API_KEY:
            print(f"[Stack-AI] API URL or KEY not configured")
            return None
            
        headers = {
            'Authorization': f'Bearer {STACK_AI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "user_id": user_id,
            "in-0": summary_text
        }
        
        print(f"[Stack-AI] Generating image for summary: {summary_text[:100]}...")
        
        response = requests.post(STACK_AI_API_URL, headers=headers, json=payload, timeout=90)
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"[Stack-AI] Raw response: {response_data}")
            
            # The Stack-AI API returns: {"outputs": {"out-0": "{'image_url': '...'}"}, ...}
            # We need to extract the image URL from this structure
            if isinstance(response_data, dict):
                # Check for outputs dictionary (Stack-AI specific format)
                if 'outputs' in response_data:
                    outputs = response_data['outputs']
                    
                    # outputs can be either a dict or a list
                    if isinstance(outputs, dict) and 'out-0' in outputs:
                        out_value = outputs['out-0']
                        print(f"[Stack-AI] Found out-0: {out_value}")
                        
                        # The value might be a string representation of a dict
                        if isinstance(out_value, str):
                            # Try to parse as Python literal (safer than eval)
                            import ast
                            try:
                                parsed = ast.literal_eval(out_value)
                                if isinstance(parsed, dict) and 'image_url' in parsed:
                                    image_url = parsed['image_url']
                                    print(f"[Stack-AI] Extracted image URL: {image_url}")
                                    return image_url
                            except (ValueError, SyntaxError) as e:
                                print(f"[Stack-AI] Could not parse out-0 as dict: {e}")
                                # Maybe it's already a URL
                                if out_value.startswith('http'):
                                    return out_value
                        
                        # If it's already a dict
                        if isinstance(out_value, dict) and 'image_url' in out_value:
                            return out_value['image_url']
                    
                    # Check if outputs is a list
                    if isinstance(outputs, list) and len(outputs) > 0:
                        output = outputs[0]
                        if isinstance(output, dict):
                            image_url = output.get('image_url') or output.get('url') or output.get('output') or output.get('value')
                            if image_url:
                                print(f"[Stack-AI] Found image URL in outputs list: {image_url}")
                                return image_url
                        elif isinstance(output, str):
                            print(f"[Stack-AI] Found image URL as string in outputs list: {output}")
                            return output
                
                # Try common direct fields
                image_url = (response_data.get('image_url') or 
                           response_data.get('url') or 
                           response_data.get('output') or 
                           response_data.get('result') or
                           response_data.get('image'))
                
                if image_url:
                    print(f"[Stack-AI] Found image URL in direct fields: {image_url}")
                    return image_url
                
                print(f"[Stack-AI] Could not extract image URL from response")
                return None
            
            # If response is already a string (possibly a URL)
            if isinstance(response_data, str):
                print(f"[Stack-AI] Response is string: {response_data}")
                if response_data.startswith('http'):
                    return response_data
            
            return None
        else:
            print(f"[Stack-AI] API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[Stack-AI] Error calling image generation: {e}")
        import traceback
        traceback.print_exc()
        return None

class Lobby:
    def __init__(self, lobby_id, host_user_id, host_username):
        self.id = lobby_id
        self.host_user_id = host_user_id
        self.host_username = host_username
        self.users = {
            host_user_id: {
                'username': host_username,
                'joined_at': datetime.now(),
                'ready': False,
                'choice': None
            }
        }
        self.max_users = 3
        self.story_messages = []
        self.events_remaining = 10
        self.story_complete = False
        self.current_round = 0
        self.created_at = datetime.now()
        self.status = 'waiting'  # waiting, playing, completed
        
    def add_user(self, user_id, username):
        if len(self.users) >= self.max_users:
            return False, "Lobby is full"
        if user_id in self.users:
            return False, "User already in lobby"
        
        self.users[user_id] = {
            'username': username,
            'joined_at': datetime.now(),
            'ready': False,
            'choice': None
        }
        return True, "User added successfully"
    
    def remove_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            # If host left, assign new host
            if user_id == self.host_user_id and self.users:
                self.host_user_id = next(iter(self.users.keys()))
            return True
        return False
    
    def set_user_ready(self, user_id, ready):
        if user_id in self.users:
            self.users[user_id]['ready'] = ready
            return True
        return False
    
    def set_user_choice(self, user_id, choice):
        if user_id in self.users:
            self.users[user_id]['choice'] = choice
            return True
        return False
    
    def all_users_ready(self):
        return len(self.users) >= 2 and all(user['ready'] for user in self.users.values())
    
    def all_users_chosen(self):
        return all(user['choice'] is not None for user in self.users.values())
    
    def reset_choices(self):
        for user in self.users.values():
            user['choice'] = None
    
    def to_dict(self):
        # Serialize users so datetime fields are JSON-safe
        users_serialized = {}
        for uid, user in self.users.items():
            users_serialized[uid] = {
                'username': user.get('username'),
                'joined_at': user.get('joined_at').isoformat() if isinstance(user.get('joined_at'), datetime) else user.get('joined_at'),
                'ready': user.get('ready', False),
                'choice': user.get('choice')
            }
        return {
            'id': self.id,
            'host_user_id': self.host_user_id,
            'host_username': self.host_username,
            'users': users_serialized,
            'max_users': self.max_users,
            'story_messages': self.story_messages,
            'events_remaining': self.events_remaining,
            'story_complete': self.story_complete,
            'current_round': self.current_round,
            'created_at': self.created_at.isoformat(),
            'status': self.status
        }

def pretty_json(data_obj, status=200):
    """Return pretty-printed JSON with stable key ordering."""
    import json
    body = json.dumps(data_obj, indent=2, sort_keys=True, ensure_ascii=False)
    return Response(body + "\n", status=status, mimetype='application/json')

# Lobby API endpoints
@app.route('/lobby/create', methods=['POST'])
def create_lobby():
    data = request.get_json()
    username = data.get('username', 'Anonymous')
    
    if not username:
        return pretty_json({'error': 'Username is required'}, 400)
    
    # Generate unique IDs
    user_id = str(uuid.uuid4())
    lobby_id = str(uuid.uuid4())[:8].upper()  # Short lobby code
    
    # Create lobby
    lobby = Lobby(lobby_id, user_id, username)
    lobbies[lobby_id] = lobby
    user_sessions[user_id] = lobby_id
    
    return pretty_json({
        'success': True,
        'lobby_id': lobby_id,
        'user_id': user_id,
        'lobby': lobby.to_dict()
    })

@app.route('/lobby/join', methods=['POST'])
def join_lobby():
    data = request.get_json()
    lobby_id = data.get('lobby_id', '').upper()
    username = data.get('username', 'Anonymous')
    
    if not lobby_id or not username:
        return pretty_json({'error': 'Lobby ID and username are required'}, 400)
    
    if lobby_id not in lobbies:
        return pretty_json({'error': 'Lobby not found'}, 404)
    
    lobby = lobbies[lobby_id]
    
    # Generate user ID
    user_id = str(uuid.uuid4())
    
    # Try to add user
    success, message = lobby.add_user(user_id, username)
    
    if success:
        user_sessions[user_id] = lobby_id
        return pretty_json({
            'success': True,
            'user_id': user_id,
            'lobby_id': lobby_id,
            'lobby': lobby.to_dict()
        })
    else:
        return pretty_json({'error': message}, 400)

@app.route('/lobby/<lobby_id>', methods=['GET'])
def get_lobby(lobby_id):
    lobby_id = lobby_id.upper()
    
    if lobby_id not in lobbies:
        return pretty_json({'error': 'Lobby not found'}, 404)
    
    return pretty_json({
        'success': True,
        'lobby': lobbies[lobby_id].to_dict()
    })

@app.route('/lobby/leave', methods=['POST'])
def leave_lobby():
    data = request.get_json()
    user_id = data.get('user_id')
    lobby_id = data.get('lobby_id', '').upper()
    
    if not user_id:
        return pretty_json({'error': 'User ID is required'}, 400)
    
    # Find lobby if not provided
    if not lobby_id and user_id in user_sessions:
        lobby_id = user_sessions[user_id]
    
    if lobby_id not in lobbies:
        return pretty_json({'error': 'Lobby not found'}, 404)
    
    lobby = lobbies[lobby_id]
    success = lobby.remove_user(user_id)
    
    if success:
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        # Clean up empty lobbies
        if len(lobby.users) == 0:
            del lobbies[lobby_id]
            return pretty_json({'success': True, 'lobby_deleted': True})
        
        return pretty_json({
            'success': True,
            'lobby': lobby.to_dict()
        })
    else:
        return pretty_json({'error': 'User not in lobby'}, 400)

@app.route('/lobby/ready', methods=['POST'])
def set_ready():
    data = request.get_json()
    user_id = data.get('user_id')
    lobby_id = data.get('lobby_id', '').upper()
    ready = data.get('ready', False)
    
    if not user_id:
        return pretty_json({'error': 'User ID is required'}, 400)
    
    # Find lobby if not provided
    if not lobby_id and user_id in user_sessions:
        lobby_id = user_sessions[user_id]
    
    if lobby_id not in lobbies:
        return pretty_json({'error': 'Lobby not found'}, 404)
    
    lobby = lobbies[lobby_id]
    success = lobby.set_user_ready(user_id, ready)
    
    if success:
        return pretty_json({
            'success': True,
            'lobby': lobby.to_dict(),
            'can_start': lobby.all_users_ready()
        })
    else:
        return pretty_json({'error': 'User not in lobby'}, 400)

@app.route('/lobby/start', methods=['POST'])
def start_lobby():
    data = request.get_json()
    lobby_id = data.get('lobby_id', '').upper()
    user_id = data.get('user_id')
    
    if not lobby_id:
        return pretty_json({'error': 'Lobby ID is required'}, 400)
    if lobby_id not in lobbies:
        return pretty_json({'error': 'Lobby not found'}, 404)
    
    lobby = lobbies[lobby_id]
    if user_id and user_id not in lobby.users:
        return pretty_json({'error': 'User not in lobby'}, 400)
    
    # Prevent multiple simultaneous start requests
    if lobby_id in starting_lobbies:
        return pretty_json({'error': 'Lobby is already starting'}, 400)
    
    # Require at least 2 players and all ready
    if len(lobby.users) < 2:
        return pretty_json({'error': 'Need at least 2 players to start'}, 400)
    if not lobby.all_users_ready():
        return pretty_json({'error': 'All players must be ready to start'}, 400)
    if lobby.status == 'playing':
        return pretty_json({'success': True, 'lobby': lobby.to_dict()})
    
    # Mark lobby as starting
    starting_lobbies.add(lobby_id)
    
    # Generate opening scene and options
    try:
        user_input = (
            f"You are a Dungeon Master starting a collaborative adventure for {len(lobby.users)} players. "
            f"Begin the story with an evocative opening in 1-2 vivid paragraphs. "
            f"This is event 1 of 10 total events. You have 9 events remaining after this one. "
            f"THEN produce a concise 50-word summary of the new scene. "
            f"THEN produce 3-4 distinct actionable next-step options for the players. "
            f"Respond ONLY as strict JSON matching this schema: {{\n"
            f"  \"story\": string,\n"
            f"  \"summary50\": string,\n"
            f"  \"options\": [string, string, string, string]\n"
            f"}} without any extra text. Session start: create opening scene and choices."
        )
        
        raw_text = call_airia_agent(user_input)
        story = None
        summary50 = None
        options = []
        if raw_text:
            try:
                parsed = extract_json_from_text(raw_text)
                if parsed is None:
                    raise ValueError('No JSON object could be decoded from model output')
                story = parsed.get('story')
                summary50 = parsed.get('summary50')
                opts = parsed.get('options')
                if isinstance(opts, list):
                    options = [str(o) for o in opts if isinstance(o, str)]
            except Exception as parse_err:
                print(f"JSON parse failed, falling back to text: {parse_err}")
                story = raw_text
        
        # Fallback story if AI fails (rate limits, etc.)
        if not story:
            story = """The ancient tavern door creaks open as you and your companions step into the dimly lit common room. The air is thick with the scent of ale and mystery. A hooded figure in the corner gestures toward your table, and you notice a weathered map spread across its surface. Your adventure begins here, in this moment of anticipation."""
            summary50 = "You enter a mysterious tavern where a hooded figure awaits with a map. The adventure begins."
            options = [
                "Approach the hooded figure and examine the map.",
                "Order drinks and listen for rumors from other patrons.",
                "Investigate the tavern's back rooms for secrets.",
                "Leave the tavern and explore the surrounding town."
            ]
        
        # Generate personalized options for each player
        player_options = {}
        option_templates = [
            ["Approach the hooded figure and examine the map.", "Order drinks and listen for rumors.", "Investigate the tavern's back rooms.", "Leave and explore the town."],
            ["Challenge the hooded figure to a game of dice.", "Search for hidden passages in the walls.", "Buy information from the bartender.", "Follow a suspicious patron outside."],
            ["Cast a detection spell to reveal secrets.", "Use stealth to eavesdrop on conversations.", "Offer to help the tavern keeper.", "Examine the map for magical properties."]
        ]
        
        for i, (uid, user_data) in enumerate(lobby.users.items()):
            template_index = i % len(option_templates)
            player_options[uid] = {
                'username': user_data['username'],
                'options': option_templates[template_index]
            }
        # Generate scene image from summary (wait for completion)
        scene_image = None
        if summary50:
            print("[Stack-AI] Waiting for image generation to complete...")
            scene_image = generate_scene_image(summary50, lobby_id)
        
        # Update lobby state
        lobby.status = 'playing'
        lobby.current_round = 1
        lobby.events_remaining = 9
        lobby.story_complete = False
        lobby.story_messages.append({
            'type': 'collaborative',
            'content': story,
            'timestamp': datetime.now().isoformat(),
            'user_choices': {},
            'summary50': summary50,
            'player_options': player_options,
            'scene_image': scene_image
        })
        # Reset ready state for next rounds
        for u in lobby.users.values():
            u['ready'] = False
            u['choice'] = None
        return pretty_json({'success': True, 'lobby': lobby.to_dict(), 'story': story, 'player_options': player_options, 'summary50': summary50, 'scene_image': scene_image})
    except Exception as e:
        return pretty_json({'error': f'Failed to start lobby: {str(e)}'}, 500)
    finally:
        # Always remove from starting set
        starting_lobbies.discard(lobby_id)

def extract_json_from_text(text):
    """Try to extract a JSON object from arbitrary text (handles code fences and extra text)."""
    import json
    if not text:
        return None
    stripped = text.strip()
    # Remove common code fences
    if stripped.startswith('```'):
        # strip first fence line
        lines = stripped.split('\n')
        # Drop first line (``` or ```json)
        lines = lines[1:]
        # Remove trailing fence if present
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]
        stripped = '\n'.join(lines).strip()
    # Heuristic: find the outermost JSON object
    start = stripped.find('{')
    end = stripped.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = stripped[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            pass
    # Final attempt: direct parse
    try:
        return json.loads(stripped)
    except Exception:
        return None


@app.route('/', methods=['GET'])
def index():
    return pretty_json({
        'status': 'ok',
        'message': 'D&D AI Backend API',
        'endpoints': ['/health', '/story', '/lobby/create', '/lobby/join', '/lobby/start']
    })

@app.route('/story', methods=['POST'])
def get_story():
    data = request.get_json()
    user_message = data.get('message', '')
    events_remaining = data.get('eventsRemaining', 10)  # Default to 10 events
    lobby_id = data.get('lobby_id', '').upper()
    user_id = data.get('user_id')
    
    if not user_message:
        return pretty_json({'error': 'Message is required'}, 400)
    
    # If this is a lobby story, handle collaborative progression
    if lobby_id and user_id:
        if lobby_id not in lobbies:
            return pretty_json({'error': 'Lobby not found'}, 404)
        
        lobby = lobbies[lobby_id]
        if user_id not in lobby.users:
            return pretty_json({'error': 'User not in lobby'}, 400)
        
        # Use lobby's current state
        events_remaining = lobby.events_remaining
        story_complete = lobby.story_complete
        
        if story_complete:
            return pretty_json({
                'story': "**THE END**\n\nYour epic collaborative adventure has reached its conclusion! All players have completed their journey together.",
                'summary50': "Collaborative story completed!",
                'options': [],
                'eventsRemaining': 0,
                'storyComplete': True,
                'lobby': lobby.to_dict()
            })
    
    try:
        # Check if story should end
        if events_remaining <= 0:
            return pretty_json({
                'story': "**THE END**\n\nYour epic adventure has reached its conclusion! You have completed all 10 events of your story. Thank you for playing!",
                'summary50': "Story completed! All 10 events finished.",
                'options': [],
                'eventsRemaining': 0,
                'storyComplete': True
            })
        
        # Ask Airia agent to return structured JSON: story, 50-word summary, and 3-4 next-step options
        user_input = (
            f"You are a Dungeon Master. Continue the user's fantasy story in 1-2 vivid paragraphs. "
            f"IMPORTANT: This is event {11 - events_remaining} of 10 total events. "
            f"{'This is the FINAL event - conclude the story with a satisfying ending!' if events_remaining == 1 else f'You have {events_remaining - 1} events remaining after this one.'} "
            f"THEN produce a concise 50-word summary of the new scene. "
            f"THEN produce 3-4 distinct actionable next-step options the user can choose, terse but evocative. "
            f"Respond ONLY as strict JSON matching this schema: {{\n"
            f"  \"story\": string,\n"
            f"  \"summary50\": string,\n"
            f"  \"options\": [string, string, string, string]\n"
            f"}} without any extra text.\n\n"
            f"User's story continuation: {user_message}"
        )

        raw_text = call_airia_agent(user_input)

        # Parse JSON with safe fallback
        import json
        story = None
        summary50 = None
        options = []
        if raw_text:
            try:
                parsed = extract_json_from_text(raw_text)
                if parsed is None:
                    raise ValueError('No JSON object could be decoded from model output')
                story = parsed.get('story')
                summary50 = parsed.get('summary50')
                opts = parsed.get('options')
                if isinstance(opts, list):
                    options = [str(o) for o in opts if isinstance(o, str)]
            except Exception as parse_err:
                print(f"JSON parse failed, falling back to text: {parse_err}")
                story = raw_text

        if not story:
            story = "I'm having trouble generating the story right now. Please try again."
        
        # Generate scene image from summary (wait for completion)
        scene_image = None
        if summary50:
            print("[Stack-AI] Waiting for image generation to complete...")
            scene_image = generate_scene_image(summary50, user_id if user_id else "solo_player")
        
        # Calculate remaining events after this one
        new_events_remaining = max(0, events_remaining - 1)
        
        # Update lobby if this is a lobby story
        lobby_data = None
        if lobby_id and user_id and lobby_id in lobbies:
            lobby = lobbies[lobby_id]
            lobby.events_remaining = new_events_remaining
            lobby.story_complete = new_events_remaining == 0
            lobby.current_round += 1
            
            # Add story message to lobby
            lobby.story_messages.append({
                'user_id': user_id,
                'username': lobby.users[user_id]['username'],
                'content': story,
                'timestamp': datetime.now().isoformat(),
                'options': options,
                'scene_image': scene_image
            })
            
            lobby_data = lobby.to_dict()
        
        return pretty_json({
            'story': story,
            'summary50': summary50,
            'options': options,
            'scene_image': scene_image,
            'eventsRemaining': new_events_remaining,
            'storyComplete': new_events_remaining == 0,
            'lobby': lobby_data
        })
        
    except Exception as e:
        return pretty_json({'error': str(e)}, 500)

@app.route('/lobby/choice', methods=['POST'])
def submit_choice():
    data = request.get_json()
    user_id = data.get('user_id')
    lobby_id = data.get('lobby_id', '').upper()
    choice = data.get('choice')
    
    if not user_id or not choice:
        return pretty_json({'error': 'User ID and choice are required'}, 400)
    
    if lobby_id not in lobbies:
        return pretty_json({'error': 'Lobby not found'}, 404)
    
    lobby = lobbies[lobby_id]
    if user_id not in lobby.users:
        return pretty_json({'error': 'User not in lobby'}, 400)
    
    # Set user's choice
    lobby.set_user_choice(user_id, choice)
    
    # Check if all users have made choices
    if lobby.all_users_chosen():
        # Generate collaborative story progression
        try:
            # Create collaborative prompt
            user_choices = []
            for uid, user_data in lobby.users.items():
                user_choices.append(f"{user_data['username']}: {user_data['choice']}")
            
            choices_text = "\n".join(user_choices)
            
            user_input = (
                f"You are a Dungeon Master managing a collaborative story with {len(lobby.users)} players. "
                f"This is event {11 - lobby.events_remaining} of 10 total events. "
                f"{'This is the FINAL event - conclude the story with a satisfying ending!' if lobby.events_remaining == 1 else f'You have {lobby.events_remaining - 1} events remaining after this one.'} "
                f"Each player has made their choice. Weave their actions together into a cohesive story continuation. "
                f"THEN produce a concise 50-word summary of the new scene. "
                f"THEN produce 3-4 distinct actionable next-step options for the next round. "
                f"Respond ONLY as strict JSON matching this schema: {{\n"
                f"  \"story\": string,\n"
                f"  \"summary50\": string,\n"
                f"  \"options\": [string, string, string, string]\n"
                f"}} without any extra text.\n\n"
                f"Player choices:\n{choices_text}\n\n"
                f"Previous story context: {lobby.story_messages[-1]['content'] if lobby.story_messages else 'Beginning of story'}"
            )
            
            # Generate story using Airia agent
            raw_text = call_airia_agent(user_input)
            
            # Parse response
            story = None
            summary50 = None
            options = []
            if raw_text:
                try:
                    parsed = extract_json_from_text(raw_text)
                    if parsed is None:
                        raise ValueError('No JSON object could be decoded from model output')
                    story = parsed.get('story')
                    summary50 = parsed.get('summary50')
                    opts = parsed.get('options')
                    if isinstance(opts, list):
                        options = [str(o) for o in opts if isinstance(o, str)]
                except Exception as parse_err:
                    print(f"JSON parse failed, falling back to text: {parse_err}")
                    story = raw_text
            
            if not story:
                story = "The collaborative story continues with the players' combined actions..."
            
            # Update lobby state
            lobby.events_remaining = max(0, lobby.events_remaining - 1)
            lobby.story_complete = lobby.events_remaining == 0
            lobby.current_round += 1
            
            # Generate personalized options for next round
            player_options = {}
            option_templates = [
                ["Investigate the mysterious sounds coming from below.", "Search for hidden treasure in the room.", "Attempt to communicate with the spirits.", "Look for secret passages in the walls."],
                ["Cast a protective spell around the group.", "Use magic to illuminate the dark corners.", "Try to dispel any curses in the area.", "Summon a familiar to scout ahead."],
                ["Draw your weapon and prepare for combat.", "Use stealth to avoid detection.", "Set up traps for potential enemies.", "Call out to announce your presence."]
            ]
            
            for i, (uid, user_data) in enumerate(lobby.users.items()):
                template_index = i % len(option_templates)
                player_options[uid] = {
                    'username': user_data['username'],
                    'options': option_templates[template_index]
                }
            
            # Generate scene image from summary (wait for completion)
            scene_image = None
            if summary50:
                print("[Stack-AI] Waiting for image generation to complete...")
                scene_image = generate_scene_image(summary50, lobby_id)
            
            # Add collaborative story message
            lobby.story_messages.append({
                'type': 'collaborative',
                'content': story,
                'timestamp': datetime.now().isoformat(),
                'user_choices': {uid: user_data['choice'] for uid, user_data in lobby.users.items()},
                'summary50': summary50,
                'player_options': player_options,
                'scene_image': scene_image
            })
            
            # Reset choices for next round
            lobby.reset_choices()
            
            return pretty_json({
                'success': True,
                'story': story,
                'summary50': summary50,
                'player_options': player_options,
                'scene_image': scene_image,
                'eventsRemaining': lobby.events_remaining,
                'storyComplete': lobby.story_complete,
                'lobby': lobby.to_dict()
            })
            
        except Exception as e:
            return pretty_json({'error': f'Failed to generate collaborative story: {str(e)}'}, 500)
    
    else:
        # Not all users have chosen yet
        return pretty_json({
            'success': True,
            'waiting_for_others': True,
            'choices_submitted': sum(1 for user in lobby.users.values() if user['choice'] is not None),
            'total_users': len(lobby.users),
            'lobby': lobby.to_dict()
        })

@app.route('/health', methods=['GET'])
def health():
    return pretty_json({'status': 'ok'})

def parse_text_for_dialogue(text):
    """
    Parse text to identify dialogue and assign voices.
    Returns list of DialogueInput objects for multivoice synthesis.
    """
    dialogue_inputs = []
    
    # Pattern to match quoted dialogue with optional speaker attribution
    # Matches: "text", 'text', or "text," the knight said
    pattern = r'([^"\']*?)(["\'])([^"\']+)\2(?:\s*[,.]?\s*([^.!?]+(?:said|asked|replied|shouted|whispered|exclaimed)[^.!?]*?))?'
    
    last_end = 0
    matches = list(re.finditer(pattern, text))
    
    if not matches:
        # No dialogue found, use single narrator voice
        return [DialogueInput(text=text.strip(), voice_id=VOICE_ROLES['narrator'])]
    
    character_voice_map = {}
    character_counter = 1
    
    for match in matches:
        narrative_before = match.group(1).strip()
        dialogue_text = match.group(3).strip()
        speaker_attr = match.group(4).strip() if match.group(4) else None
        
        # Add narrative before dialogue
        if narrative_before:
            dialogue_inputs.append(
                DialogueInput(text=narrative_before, voice_id=VOICE_ROLES['narrator'])
            )
        
        # Determine voice for dialogue
        voice_id = VOICE_ROLES['narrator']
        
        if speaker_attr:
            # Try to identify speaker from attribution
            speaker_lower = speaker_attr.lower()
            
            # Assign voices based on keywords
            if any(word in speaker_lower for word in ['monster', 'dragon', 'beast', 'creature', 'demon']):
                voice_id = VOICE_ROLES['monster']
            elif speaker_attr not in character_voice_map:
                # Assign a character voice in rotation
                voice_key = f'character{((character_counter - 1) % 3) + 1}'
                character_voice_map[speaker_attr] = VOICE_ROLES[voice_key]
                character_counter += 1
                voice_id = character_voice_map[speaker_attr]
            else:
                voice_id = character_voice_map[speaker_attr]
        else:
            # No speaker attribution, alternate between character voices
            voice_key = f'character{((len(dialogue_inputs) % 3) + 1)}'
            voice_id = VOICE_ROLES[voice_key]
        
        # Add dialogue with assigned voice
        dialogue_inputs.append(
            DialogueInput(text=dialogue_text, voice_id=voice_id)
        )
        
        last_end = match.end()
    
    # Add any remaining narrative after last dialogue
    remaining = text[last_end:].strip()
    if remaining:
        dialogue_inputs.append(
            DialogueInput(text=remaining, voice_id=VOICE_ROLES['narrator'])
        )
    
    return dialogue_inputs

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """Generate speech audio from text using ElevenLabs multivoice API"""
    if not elevenlabs_client:
        return pretty_json({'error': 'ElevenLabs API key not configured. Add ELEVENLABS_API_KEY to backend/.env'}, 500)
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return pretty_json({'error': 'Text is required'}, 400)
    
    try:
        # Parse text and create dialogue inputs with multiple voices
        dialogue_inputs = parse_text_for_dialogue(text)
        
        # Generate audio using ElevenLabs
        # Note: text-to-dialogue requires v3 models, so we'll use single voice with turbo model
        # For now, use single narrator voice for simplicity and speed
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ROLES['narrator'],
            model_id="eleven_turbo_v2_5",
            output_format="mp3_44100_128",
        )
        
        # Collect the audio stream into bytes
        audio_bytes = b''
        for chunk in audio_generator:
            if chunk:
                audio_bytes += chunk
        
        # Return audio as response
        return Response(
            audio_bytes,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': 'inline; filename=speech.mp3',
                'Content-Type': 'audio/mpeg'
            }
        )
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        import traceback
        traceback.print_exc()
        return pretty_json({'error': f'Failed to generate speech: {str(e)}'}, 500)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8001))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)