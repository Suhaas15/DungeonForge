# 🎨 AI Dungeon Master Features

## What's New

Your AI Dungeon Master is now powered by Airia's intelligent agent platform!

## How It Works

1. **User sends a message** → "You enter a dragon's lair"
2. **Backend formats prompt** → Adds Dungeon Master context and instructions
3. **Airia agent processes** → Your custom agent generates the story
4. **Backend parses response** → Extracts story, summary, and options
5. **Frontend displays** → Story text + action choices

## Backend Implementation

### Main Endpoints
- `/story` - Solo story continuation
  - Accepts: `{ message: string, generateImage: boolean, eventsRemaining: number }`
  - Returns: `{ story: string, summary50: string, options: array, imageUrl: string | null }`

- `/lobby/start` - Start collaborative game
- `/lobby/choice` - Submit player choice in collaborative mode

### Core Functions
- `call_airia_agent(user_input)` - Communicates with Airia Pipeline API
- `generate_image_prompt(story_text)` - Creates image descriptions (optional)
- `generate_scene_image(prompt)` - Placeholder for image generation

### AI Integration
- **Platform**: Airia.ai custom agent
- **Pipeline ID**: 74d3e775-1b60-42f2-be75-e3fb963a5e02
- **Response Format**: Structured JSON with story, summary, and options

## Frontend Implementation

### New Features
- **Two buttons**: "Send" and "🎨 With Image"
- **Image display**: Shows DALL-E generated scenes in chat
- **Loading states**: Different messages for text vs image generation

### UI Updates
- Scene images appear below AI messages
- Styled with shadows and rounded corners
- Responsive image sizing

## Performance Considerations

- **Response time**: Depends on your Airia agent configuration (typically 2-5 seconds)
- **Story generation**: One API call per story continuation
- **Collaborative mode**: One API call per round (all player choices combined)
- **Image generation**: Currently disabled (can be enabled with additional integration)

## Usage Tips

1. **Use "Continue Story" for text-only** generation (faster)
2. **Use "With Scene Art"** if you've configured image generation
3. **Be descriptive in your prompts** for richer story narratives
4. **Configure your Airia agent** to respond in the expected JSON format for best results

## Example Prompts That Work Well

✅ "You discover an ancient temple deep in the jungle"
✅ "The dragon awakens from its slumber in the treasure room"
✅ "A mysterious portal opens in the center of the village"
✅ "You find a magical sword glowing in the moonlight"

## Technical Details

- **API Communication**: Direct HTTP POST to Airia Pipeline API
- **No storage**: All data is ephemeral, stored only in memory during game session
- **CORS enabled**: Frontend can communicate with backend on different ports
- **Error handling**: Graceful fallback if Airia agent is unavailable
- **JSON parsing**: Flexible parsing to handle various response formats
- **Timeout**: 30 seconds default (configurable for slower agents)
