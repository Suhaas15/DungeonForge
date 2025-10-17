# 📖 AI Dungeon Master Storybook

A beautiful storybook interface where you co-create epic adventures with AI! Powered by your custom Airia agent for intelligent story generation.

## ✨ Features

- 📝 AI-powered story continuation with Airia agent
- 🎨 Optional AI-generated fantasy scene images (configurable)
- 📖 Beautiful storybook UI - AI writes on left page, you write on right
- ⚡ Real-time story generation
- 🎭 Immersive Dungeon Master experience
- 👥 Collaborative multiplayer mode (2-3 players)

## Setup

1. Add your Airia API credentials to `.env`:
```
AIRIA_API_KEY=your-airia-api-key-here
AIRIA_USER_ID=your-airia-user-id-here
```

2. Install backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

3. Install frontend:
```bash
cd frontend
npm install
npm start
```

## Usage

- Backend runs on: http://localhost:8001
- Frontend runs on: http://localhost:3000

**Two ways to continue your story:**
1. **📝 Continue Story** - Get story text only (fast)
2. **🎨 With Scene Art** - Get story text + AI-generated fantasy scene image (if available)

## How It Works

The interface looks like an **open storybook**:
- **Left Page**: The AI Dungeon Master writes your story
- **Right Page**: You write your actions and responses
- **Bottom**: Input area to continue the adventure

## Example

Type: "You enter a dark cave filled with glowing crystals"

- Click **📝 Continue Story**: Get story continuation
- Click **🎨 With Scene Art**: Get story + beautiful fantasy scene image!

## Commands to Run

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```