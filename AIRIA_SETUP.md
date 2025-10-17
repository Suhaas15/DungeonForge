# 🤖 Airia Agent Setup Guide

## Overview

This project uses your custom Airia agent to power the AI Dungeon Master functionality. The agent handles story generation, narrative continuation, and collaborative storytelling.

## Prerequisites

- Airia account with access to the Pipeline API
- Your Airia agent/pipeline ID: `74d3e775-1b60-42f2-be75-e3fb963a5e02`
- API key for Airia platform

## Quick Setup

### 1️⃣ Get Your Airia Credentials

You need two pieces of information:

1. **AIRIA_API_KEY**: Your API key for accessing the Airia platform
2. **AIRIA_USER_ID**: Your user ID (can be any identifier, defaults to `dungeon-master-user`)

### 2️⃣ Configure Environment Variables

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` and add your credentials:
```env
# Airia Configuration
AIRIA_API_KEY=your_actual_airia_api_key_here
AIRIA_USER_ID=your_airia_user_id_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 3️⃣ Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4️⃣ Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm start
```

### 5️⃣ Test It Out

Navigate to http://localhost:3000 and start your adventure!

## How It Works

### Agent Communication

The backend communicates with your Airia agent using the Pipeline Execution API:

```python
POST https://api.airia.ai/v2/PipelineExecution/74d3e775-1b60-42f2-be75-e3fb963a5e02

Headers:
  X-API-KEY: your_airia_api_key
  Content-Type: application/json

Body:
{
  "userId": "your_user_id",
  "userInput": "story prompt or instruction",
  "asyncOutput": false
}
```

### Story Generation Flow

1. **User Input** → Frontend sends user's story action
2. **Backend Processing** → Formats prompt with Dungeon Master instructions
3. **Airia Agent** → Processes the prompt and generates story
4. **Response Parsing** → Extracts story, summary, and options
5. **Frontend Display** → Shows the generated story to the user

### Expected Response Format

Your Airia agent should return responses in this JSON format:

```json
{
  "story": "The vivid story continuation in 1-2 paragraphs...",
  "summary50": "A concise 50-word summary of the scene...",
  "options": [
    "Option 1: First action choice",
    "Option 2: Second action choice",
    "Option 3: Third action choice",
    "Option 4: Fourth action choice"
  ]
}
```

## Agent Configuration Tips

### For Best Results

Configure your Airia agent to:

1. **Act as a Dungeon Master**: Use fantasy RPG storytelling style
2. **Generate Structured Output**: Return JSON with `story`, `summary50`, and `options` fields
3. **Track Story Progress**: Be aware of event counts (1-10 events per game)
4. **Weave Multiple Inputs**: For collaborative mode, combine multiple player choices
5. **Be Vivid and Descriptive**: Create immersive, engaging narratives

### Example Prompts

The system sends prompts like this to your agent:

**Solo Mode:**
```
You are a Dungeon Master. Continue the user's fantasy story in 1-2 vivid paragraphs.
IMPORTANT: This is event 3 of 10 total events. You have 7 events remaining after this one.
THEN produce a concise 50-word summary of the new scene.
THEN produce 3-4 distinct actionable next-step options the user can choose.
Respond ONLY as strict JSON matching this schema:
{
  "story": string,
  "summary50": string,
  "options": [string, string, string, string]
}

User's story continuation: You enter a dark cave filled with glowing crystals
```

**Collaborative Mode:**
```
You are a Dungeon Master managing a collaborative story with 3 players.
This is event 2 of 10 total events. You have 8 events remaining.
Each player has made their choice. Weave their actions together into a cohesive story.
...
Player choices:
Alice: Investigate the ancient altar
Bob: Search for hidden treasures
Charlie: Stand guard at the entrance
```

## Image Generation (Optional)

Currently, image generation is disabled. To enable it:

1. Configure your Airia agent to support image generation requests
2. Or integrate with an external image service (DALL-E, Stable Diffusion, etc.)
3. Update the `generate_scene_image()` function in `backend/app.py`

## Troubleshooting

### "Connection refused" or API errors

**Check your API key:**
```bash
# In backend directory
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('AIRIA_API_KEY')[:10] + '...' if os.getenv('AIRIA_API_KEY') else 'NOT FOUND')"
```

**Test the API directly:**
```bash
curl -X POST https://api.airia.ai/v2/PipelineExecution/74d3e775-1b60-42f2-be75-e3fb963a5e02 \
  -H "X-API-KEY: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","userInput":"Hello","asyncOutput":false}'
```

### Agent returns unexpected format

If the agent doesn't return JSON in the expected format, the app will:
1. Try to extract JSON from the text
2. Fall back to using the raw text as the story
3. Provide default options if none are available

**To fix:** Update your Airia agent's system prompt to ensure it returns valid JSON.

### Timeout errors

The default timeout is 30 seconds. If your agent takes longer:

Edit `backend/app.py` line ~41:
```python
response = requests.post(AIRIA_PIPELINE_URL, headers=headers, data=payload, timeout=60)  # Increase to 60 seconds
```

### "No story generated"

This usually means:
- API key is incorrect
- Network connectivity issues
- Airia service is down
- Agent pipeline ID is wrong

Check the backend console logs for detailed error messages.

## Cost Considerations

Airia pricing depends on your account and agent configuration. Each story continuation makes one API call to your agent.

**Typical usage per game:**
- Solo mode: 10 API calls (one per event)
- Collaborative mode: 10 API calls (one per round)
- Image prompt generation: +10 calls if enabled

**Check your usage:** Visit your Airia dashboard to monitor API usage and costs.

## Advanced Configuration

### Custom Pipeline URL

To use a different Airia pipeline, edit `backend/app.py` line ~20:

```python
AIRIA_PIPELINE_URL = "https://api.airia.ai/v2/PipelineExecution/YOUR_PIPELINE_ID"
```

### Async Output

For faster response times with large agents, you can enable async mode:

Edit `backend/app.py` in the `call_airia_agent()` function:
```python
"asyncOutput": True  # Change from False to True
```

Then implement polling logic to get the result.

### Custom Response Parsing

If your agent returns a different format, update the `call_airia_agent()` function in `backend/app.py` to parse your specific response structure.

## Support

- **Airia Documentation**: [Airia AI Docs](https://docs.airia.ai/)
- **Pipeline API**: [API Reference](https://api.airia.ai/docs)
- **Backend Logs**: Check terminal running `python app.py` for detailed error messages
- **Frontend Logs**: Open browser console (F12) for frontend errors

## What's Different from OpenAI Version?

### Advantages
✅ Custom agent tailored to your needs
✅ Full control over model and behavior
✅ No token counting or model limits
✅ Can integrate with your own data/knowledge base

### Considerations
⚠️ Response time depends on your agent configuration
⚠️ JSON format must be configured in agent
⚠️ Image generation requires separate integration

---

**Your AI Dungeon Master is ready to create epic adventures with Airia! 🎭✨**

