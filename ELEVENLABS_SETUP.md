# ElevenLabs Text-to-Speech Integration Guide

## ✨ New Features Implemented

### 1. 🐉 Dragon-Themed Font
- Added medieval fantasy fonts from Google Fonts
- **MedievalSharp** for body text
- **Cinzel Decorative** for titles and headers
- Gives the app an authentic D&D feel

### 2. 📜 Synchronized Scrolling
- Left page (AI messages) and right page (user messages) now scroll in correlation
- When you scroll one page, the other page follows proportionally
- Creates a more cohesive reading experience

### 3. 🔊 ElevenLabs Multivoice Text-to-Speech
- Audio narration for all AI Dungeon Master messages with **multiple character voices**
- Click the speaker button (🔊) next to any AI message to hear it narrated
- **Intelligent voice assignment**:
  - Narrator voice (George) for narrative text
  - Different character voices for dialogue in quotes
  - Special monster/dragon voice for creature dialogue
  - Automatically detects and assigns voices based on context
- Loading indicator (⏳) while audio is being generated
- Play/pause functionality (⏸️) while audio is playing

## 🚀 Setup Instructions

### Step 1: Get Your ElevenLabs API Key

1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up or log in
3. Navigate to your [profile settings](https://elevenlabs.io/app/settings/api)
4. Copy your API key

### Step 2: Configure Your Environment

1. Create a `.env` file in the `/backend` directory if it doesn't exist:
   ```bash
   cd backend
   cp ../env.example .env
   ```

2. Add your ElevenLabs API key to the `.env` file:
   ```
   ELEVENLABS_API_KEY=your_actual_api_key_here
   ```

### Step 3: Install Dependencies

The ElevenLabs SDK has already been added to `requirements.txt` and installed. If you need to reinstall:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Test the Feature

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Play through a story and click the 🔊 button on any AI message!

## 🎮 How to Use

### Audio Buttons
- **🔊 Speaker Icon**: Click to generate and play audio narration
- **⏳ Hourglass**: Audio is being generated (please wait)
- **⏸️ Pause Icon**: Audio is currently playing (click again to stop)

### Features:
- Only one audio can play at a time
- Audio automatically stops when you play a new message
- Click the playing audio button again to stop it
- Audio quality is optimized for streaming (MP3 format)

## 🎭 Multivoice System

The app now uses **ElevenLabs Text-to-Dialogue** API with multiple voices:

### Voice Roles:
- **Narrator**: George (British narrator) - for narrative text
- **Character 1**: Sarah (Female) - for first character dialogue
- **Character 2**: Daniel (Male) - for second character dialogue  
- **Character 3**: Rachel (Female) - for third character dialogue
- **Monster/Dragon**: Josh (Deep male) - for creature dialogue

### How It Works:
1. Text is automatically parsed to detect dialogue in quotes
2. Narrative text uses the narrator voice
3. Quoted dialogue gets assigned character voices
4. Keywords like "dragon", "monster", "beast" trigger the monster voice
5. Multiple characters are tracked and assigned consistent voices

### Want to Change the Voices?

Edit the `VOICE_ROLES` dictionary in `/backend/app.py` (lines 30-36):
```python
VOICE_ROLES = {
    'narrator': 'JBFqnCBsd6RMkjVDRZzb',  # Change to your preferred narrator
    'character1': 'EXAVITQu4vr4xnSDxMaL',  # Change to your preferred voice
    'character2': 'onwK4e9ZLuTAKqWW03F9',  # Change to your preferred voice
    'character3': 'TX3LPaxmHKxFdv7VOQHJ',  # Change to your preferred voice
    'monster': '21m00Tcm4TlvDq8ikWAM',  # Change to your preferred voice
}
```

Find more voices at: https://elevenlabs.io/voice-library

## 📊 Technical Details

### Backend Endpoint
- **Route**: `POST /text-to-speech`
- **Request**: `{ "text": "Your text here" }`
- **Response**: Audio file (MP3 format)
- **API Used**: ElevenLabs `text_to_dialogue.convert()` for multivoice
- **Fallback**: Single voice `text_to_speech.convert()` for simple text

### Text Parsing Algorithm
- Regex pattern detects quoted dialogue and speaker attribution
- Supports both double quotes (`"text"`) and single quotes (`'text'`)
- Identifies speakers from phrases like "said", "asked", "replied", etc.
- Maintains character-to-voice mapping for consistency across story
- Special keyword detection for monster/creature voices

### Frontend Implementation
- Audio buttons integrated into AI message components
- State management for playing/loading status
- Automatic cleanup of audio resources
- Error handling with user-friendly messages

## 💡 Tips

1. **First Load**: The first audio generation might take 2-3 seconds as it connects to ElevenLabs
2. **Rate Limits**: Free tier has character limits. Check your [ElevenLabs usage](https://elevenlabs.io/app/usage)
3. **Audio Quality**: Using `mp3_44100_128` for balanced quality and speed
4. **Cost**: Each character costs credits. Multivoice uses more credits than single voice
5. **Best Results**: Stories with dialogue in quotes will trigger multivoice narration
6. **Voice Consistency**: The system remembers which character gets which voice within a story segment

## 🐛 Troubleshooting

### Audio Button Shows Error
- ✅ Check that your `ELEVENLABS_API_KEY` is set in `.env`
- ✅ Restart the backend server after adding the key
- ✅ Check your ElevenLabs account has available credits

### Audio Not Playing
- ✅ Check browser console for errors
- ✅ Ensure your browser allows audio playback
- ✅ Try a different browser (Chrome/Firefox recommended)

### Synchronized Scrolling Issues
- ✅ Make sure both pages have content
- ✅ Try manually scrolling one page to trigger sync
- ✅ Refresh the page if scrolling feels stuck

## 📚 Resources

- [ElevenLabs Documentation](https://elevenlabs.io/docs/quickstart)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [Voice Library](https://elevenlabs.io/voice-library)
- [API Pricing](https://elevenlabs.io/pricing)

## 🎉 Enjoy Your Enhanced D&D Experience!

Your Dungeon Master can now literally speak to you! The dragon font adds atmosphere, synchronized scrolling keeps you immersed, and audio narration brings your adventures to life.

Happy adventuring! 🐉⚔️🎲

