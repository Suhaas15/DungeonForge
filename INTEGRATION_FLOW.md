# Stack AI Integration - Complete Flow Diagram

## End-to-End Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION                                │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
            User submits action: "I explore the dark forest"
                                    │
                                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                                │
│  App.js / LobbyRoom.js                                                   │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓ POST /story
                    {
                      "message": "I explore the dark forest",
                      "eventsRemaining": 9,
                      "user_id": "abc123"
                    }
                                    │
                                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (Flask)                                 │
│  app.py - /story endpoint                                                │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ↓                               ↓
         ┌─────────────────────┐       ┌──────────────────────┐
         │   call_airia_agent   │       │  (Wait for Airia)    │
         │  (Airia AI Agent)    │       │                      │
         └─────────────────────┘       └──────────────────────┘
                    │
                    ↓
         Returns JSON with:
         {
           "story": "As you venture into the shadows of the ancient 
                     forest, twisted trees loom overhead. The air 
                     grows cold, and you hear whispers in the wind...",
           "summary50": "You enter a dark forest with twisted trees,
                        cold air, and mysterious whispers in the wind.",
           "options": [
             "Follow the whispers deeper into the forest",
             "Light a torch and search for a path",
             "Climb a tree to survey the area"
           ]
         }
                    │
                    ↓
         Extract summary50: "You enter a dark forest with twisted 
                            trees, cold air, and mysterious whispers..."
                    │
                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│              generate_scene_image(summary50, user_id)                    │
│              (Stack AI Integration)                                      │
└──────────────────────────────────────────────────────────────────────────┘
                    │
                    ↓ POST to Stack AI API
         {
           "user_id": "abc123",
           "in-0": "You enter a dark forest with twisted trees..."
         }
                    │
                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    STACK AI API                                          │
│  (DALL-E Image Generation)                                               │
└──────────────────────────────────────────────────────────────────────────┘
                    │
                    ↓ (5-15 seconds)
         Stack AI Response:
         {
           "outputs": {
             "out-0": "{'image_url': 'https://oaidalleapiprodscus...'}"
           },
           "run_id": "...",
           "metadata": null
         }
                    │
                    ↓
         Parse string dictionary using ast.literal_eval()
         Extract image_url: "https://oaidalleapiprodscus.blob.core..."
                    │
                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                  BACKEND RESPONSE ASSEMBLY                               │
└──────────────────────────────────────────────────────────────────────────┘
                    │
                    ↓
         Complete Response:
         {
           "story": "As you venture into the shadows...",
           "summary50": "You enter a dark forest with twisted trees...",
           "options": [...],
           "scene_image": "https://oaidalleapiprodscus.blob.core...",
           "eventsRemaining": 8,
           "storyComplete": false
         }
                    │
                    ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND RENDERING                                    │
└──────────────────────────────────────────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ↓                     ↓
┌─────────────────┐   ┌─────────────────────┐
│   LEFT PAGE     │   │   RIGHT PAGE        │
│                 │   │                     │
│ 🎭 DM's Tale    │   │ 📝 Your Adventure   │
│                 │   │                     │
│ [Story Text]    │   │ [Your Actions]      │
│                 │   │                     │
│                 │   │ ┌─────────────────┐ │
│                 │   │ │ 🎨 Scene Visual │ │
│                 │   │ │                 │ │
│                 │   │ │  [🖼️ Image]     │ │
│                 │   │ │                 │ │
│                 │   │ └─────────────────┘ │
│                 │   │                     │
│                 │   │ [Action Options]    │
└─────────────────┘   └─────────────────────┘
```

## Key Integration Points

### 1. Backend Endpoints

#### `/story` - Solo Mode Story Generation
```python
# Lines 559-676 in app.py
@app.route('/story', methods=['POST'])
def get_story():
    # 1. Get Airia response with summary
    raw_text = call_airia_agent(user_input)
    parsed = extract_json_from_text(raw_text)
    summary50 = parsed.get('summary50')
    
    # 2. Generate scene image
    scene_image = generate_scene_image(summary50, user_id)
    
    # 3. Return with image URL
    return {
        'story': story,
        'scene_image': scene_image,  # ← Image URL
        ...
    }
```

#### `/lobby/start` - Lobby Opening Scene
```python
# Lines 399-513 in app.py
@app.route('/lobby/start', methods=['POST'])
def start_lobby():
    # Generate opening scene and image
    scene_image = generate_scene_image(summary50, lobby_id)
    
    lobby.story_messages.append({
        'content': story,
        'scene_image': scene_image,  # ← Stored in lobby
        ...
    })
```

#### `/lobby/choice` - Collaborative Story Progression
```python
# Lines 684-800 in app.py
@app.route('/lobby/choice', methods=['POST'])
def submit_choice():
    # When all players choose
    if lobby.all_users_chosen():
        # Generate collaborative story
        scene_image = generate_scene_image(summary50, lobby_id)
        
        lobby.story_messages.append({
            'scene_image': scene_image,  # ← Image for new scene
            ...
        })
```

### 2. Frontend Components

#### Solo Mode - `App.js`
```javascript
// Line 110: Receive scene image
setCurrentSceneImage(data.scene_image);

// Lines 362-379: Display image
{!isLoading && currentSceneImage && (
  <div className="scene-image-panel">
    <div className="scene-image-title">🎨 Scene Visualization</div>
    <img src={currentSceneImage} alt="Generated scene" />
  </div>
)}
```

#### Lobby Mode - `LobbyRoom.js`
```javascript
// Lines 284-301: Display latest scene image
{!isLoading && lobby.story_messages.length > 0 && 
 lobby.story_messages[lobby.story_messages.length - 1].scene_image && (
  <div className="scene-image-container">
    <h4>🎨 Scene Visualization</h4>
    <img src={lobby.story_messages[...].scene_image} />
  </div>
)}
```

## Timing Diagram

```
Time →
────────────────────────────────────────────────────────────────────

t=0s    : User clicks "Continue Story"
          │
t=0.1s  : Frontend sends POST /story
          │
t=0.2s  : Backend receives request
          │
t=0.3s  : Backend calls Airia AI
          │
t=2-5s  : ▓▓▓▓▓▓ Airia generates story ▓▓▓▓▓▓
          │
t=5s    : Airia returns story + summary
          │
t=5.1s  : Backend extracts summary50
          │
t=5.2s  : Backend calls Stack AI with summary
          │
t=6-20s : ▓▓▓▓▓▓▓▓▓ Stack AI generates image ▓▓▓▓▓▓▓▓▓
          │      (DALL-E image generation)
          │
t=20s   : Stack AI returns image URL
          │
t=20.1s : Backend parses response, extracts URL
          │
t=20.2s : Backend returns complete response to frontend
          │
t=20.3s : Frontend receives response
          │
t=20.4s : React updates state with image URL
          │
t=20.5s : Browser loads image from Azure
          │
t=21s   : ✅ Image displays to user

Total: ~21 seconds (story generation + image generation)
```

## Error Handling Flow

```
┌─────────────────────┐
│ Image Generation    │
│ Request             │
└─────────────────────┘
          │
          ↓
    ┌─────────┐
    │ API Call│
    └─────────┘
          │
    ┌─────┴─────┐
    │           │
    ↓           ↓
  Success    Failure
    │           │
    ↓           ↓
Return URL   Return None
    │           │
    ↓           ↓
Frontend    Frontend
Displays    Hides
Image       Image
            Panel
    │           │
    ↓           ↓
  ✅ User     Story
  Sees       Continues
  Image      Normally
```

## Data Structure Evolution

### Before Integration
```javascript
{
  "story": "...",
  "options": [...],
  "eventsRemaining": 9
}
```

### After Integration
```javascript
{
  "story": "...",
  "summary50": "...",          // ← New: 50-word summary
  "options": [...],
  "scene_image": "https://...", // ← New: Generated image URL
  "eventsRemaining": 9
}
```

## Summary

The Stack AI integration follows this flow:

1. **User Action** → Triggers story generation
2. **Airia AI** → Generates story + 50-word summary
3. **Stack AI** → Generates image from summary (DALL-E)
4. **Backend** → Extracts image URL, returns complete response
5. **Frontend** → Displays image on right side of page

**Total Time**: 5-20 seconds  
**Display Location**: Right page, "Scene Visualization" section  
**Status**: ✅ Fully integrated and tested  

---

*Flow diagram created: October 17, 2025*

