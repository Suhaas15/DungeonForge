# Stack AI Integration - Quick Start Guide

## What Was Done

✅ **Backend Integration Complete**
- Stack AI API calls integrated in `backend/app.py`
- Image URL extraction from API response (parses string-formatted dictionary)
- Images generated from Airia's 50-word story summaries
- Integration added to all story generation endpoints

✅ **Frontend Display Complete**
- Scene visualization panel added to both Solo and Lobby modes
- Loading spinner shows during image generation
- Images display on the right side above action options
- Graceful error handling if images fail to load

✅ **Testing Tools Provided**
- Test script: `backend/test_stackai.py`
- Comprehensive documentation: `STACKAI_INTEGRATION.md`

## Quick Test

### 1. Test Stack AI API Directly

```bash
cd backend
python3 test_stackai.py
```

Expected output:
```
✅ Extracted Image URL: https://oaidalleapiprodscus.blob.core.windows.net/...
```

### 2. Test in Application

**Start Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Start Frontend (new terminal):**
```bash
cd frontend
npm start
```

**Test the Feature:**
1. Open http://localhost:3000
2. Choose "Solo Adventure"
3. Enter a story prompt (e.g., "I wake up in a mysterious forest")
4. Wait for response
5. Look for "🎨 Scene Visualization" section on the right page
6. Image should appear within 5-10 seconds

## Where Images Appear

### Solo Mode
- **Location**: Right page, above action options
- **Shows**: Generated scene from current story moment
- **Updates**: Every time you submit a new action

### Lobby Mode
- **Location**: Right column, above player choices
- **Shows**: Collaborative scene visualization
- **Updates**: When all players make choices and story advances

## How It Works

```
Your Action
    ↓
Airia AI generates story + summary
    ↓
Stack AI generates image from summary
    ↓
Image displays in "Scene Visualization"
```

## Architecture

```
┌─────────────────┐
│  Airia Agent    │ ─→ Story + 50-word Summary
└─────────────────┘
         │
         ↓
┌─────────────────┐
│  Stack AI Agent │ ─→ DALL-E Image URL
└─────────────────┘
         │
         ↓
┌─────────────────┐
│  Frontend       │ ─→ Display Image
└─────────────────┘
```

## Key Files Modified

1. **`backend/app.py`**
   - `generate_scene_image()` function (lines 79-172)
   - Integration in `/story` endpoint (line 586)
   - Integration in `/lobby/start` endpoint (line 432)
   - Integration in `/lobby/choice` endpoint (line 718)

2. **`frontend/src/App.js`**
   - Scene image state management (line 13)
   - Scene visualization panel (lines 352-379)
   - Debug logging (lines 112-118)

3. **`frontend/src/LobbyRoom.js`**
   - Scene image display (lines 274-301)
   - Loading states

4. **`frontend/src/index.css`**
   - Scene image styling (lines 675-728)
   - Loading spinner animation (lines 717-728)

## Debugging

### Check Backend Logs

When running the backend, you'll see:
```
[Stack-AI] Generating image for summary: ...
[Stack-AI] Raw response: {...}
[Stack-AI] Found out-0: ...
[Stack-AI] Extracted image URL: https://...
```

### Check Browser Console

Open Developer Tools (F12) and look for:
```javascript
Story response received: {
  hasStory: true,
  hasSummary: true,
  hasSceneImage: true,
  sceneImage: "https://..."
}
```

## Troubleshooting

### ❌ Images Not Showing

**Check 1**: Backend Running?
```bash
# Should see: Running on http://0.0.0.0:8001
```

**Check 2**: API Working?
```bash
cd backend
python3 test_stackai.py
# Should see: ✅ Extracted Image URL
```

**Check 3**: Browser Console Errors?
```
F12 → Console tab
Look for red errors related to images
```

### ⚠️ Images Load Slowly

This is normal! DALL-E image generation takes 5-15 seconds.
- Loading spinner shows progress
- Be patient and wait

### ⚠️ Image URLs Expire

Azure DALL-E URLs expire after ~2 hours.
- Images regenerated on new story actions
- This is expected behavior

## API Details

**Stack AI Endpoint:**
```
POST https://api.stack-ai.com/inference/v0/run/74329701-0f1c-429f-94f2-1a8bff522ae5/68f2b40560ba42fb86bdcc9b
```

**Request:**
```json
{
  "user_id": "user_id_here",
  "in-0": "50-word scene summary"
}
```

**Response:**
```json
{
  "outputs": {
    "out-0": "{'image_url': 'https://...'}"
  }
}
```

## What's Next?

The integration is **complete and ready to use**! 

### Optional Enhancements:

1. **Add to `.env` file** (for security):
   ```env
   STACK_AI_API_KEY=your_key_here
   ```

2. **Customize Image Styles**:
   - Modify summary text format
   - Add style keywords (e.g., "fantasy art", "oil painting")

3. **Cache Images**:
   - Store generated images
   - Reuse for similar scenes

## Support

For issues or questions:
1. Check `STACKAI_INTEGRATION.md` for detailed docs
2. Run `test_stackai.py` to verify API connectivity
3. Check backend logs for `[Stack-AI]` messages
4. Check browser console for errors

---

**Integration Status: ✅ COMPLETE AND TESTED**

The Stack AI image generation is fully integrated and working. Images will appear in the "🎨 Scene Visualization" section on the right side of the page for both Solo and Lobby game modes.

