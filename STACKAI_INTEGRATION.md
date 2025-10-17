# Stack AI Image Generation Integration

This document describes the integration of Stack AI's image generation API into the D&D AI storytelling application.

## Overview

The Stack AI agent generates fantasy scene images based on story summaries from the Airia AI storytelling agent. Images are displayed alongside the story text to enhance the immersive experience.

## Integration Components

### Backend Integration (`backend/app.py`)

#### Configuration
```python
STACK_AI_API_URL = "https://api.stack-ai.com/inference/v0/run/74329701-0f1c-429f-94f2-1a8bff522ae5/68f2b40560ba42fb86bdcc9b"
STACK_AI_API_KEY = "2cca805e-ef0f-4c2c-990a-389db4d098d3"
```

#### Function: `generate_scene_image(summary_text, user_id)`
- **Purpose**: Calls the Stack AI API to generate an image from a scene summary
- **Input**: 50-word scene summary from Airia's output
- **Output**: Image URL (Azure DALL-E blob storage URL)
- **Response Format**: 
  ```json
  {
    "outputs": {
      "out-0": "{'image_url': 'https://...'}"
    }
  }
  ```
- **Key Feature**: Parses the string-formatted dictionary using Python's `ast.literal_eval()`

#### Integration Points

1. **Solo Mode Story Generation** (`/story` endpoint)
   - When Airia generates a story continuation, the `summary50` field is extracted
   - `generate_scene_image()` is called with the summary
   - The resulting image URL is returned in the response as `scene_image`

2. **Lobby Mode - Story Start** (`/lobby/start` endpoint)
   - Initial scene image is generated for the opening story
   - Image URL is stored in lobby data structure

3. **Lobby Mode - Collaborative Choices** (`/lobby/choice` endpoint)
   - When all players make choices and a new scene is generated
   - Image is generated from the scene summary
   - Image URL is added to the story message

### Frontend Integration

#### Solo Mode (`frontend/src/App.js`)

**Display Location**: Right page, above action options
- Shows loading spinner while image is being generated
- Displays image when loaded
- Handles errors gracefully (hides image on load failure)

**State Management**:
```javascript
const [currentSceneImage, setCurrentSceneImage] = useState(null);
```

#### Lobby Mode (`frontend/src/LobbyRoom.js`)

**Display Location**: Right column of story layout, above action options
- Same loading and error handling as solo mode
- Image updates when new collaborative story scenes are generated

### CSS Styling (`frontend/src/index.css`)

**Scene Image Panel**:
- Medieval-themed border and styling
- Loading spinner animation
- Responsive design
- Image sizing and shadow effects

**Classes**:
- `.scene-image-panel` - Container styling
- `.scene-image-title` - Title styling
- `.scene-image` - Image display styling
- `.image-loading` - Loading state display
- `.spinner` - Animated loading spinner

## Workflow

### Story Generation with Image

```
1. User submits action/choice
   ↓
2. Airia generates story + summary50
   ↓
3. summary50 passed to Stack AI
   ↓
4. Stack AI generates DALL-E image
   ↓
5. Image URL extracted from response
   ↓
6. URL returned to frontend
   ↓
7. Frontend displays image
```

### Data Flow

```
Airia Output:
{
  "story": "Full narrative text...",
  "summary50": "Concise 50-word summary",
  "options": ["option1", "option2", ...]
}
      ↓
Stack AI Input:
{
  "user_id": "user123",
  "in-0": "Concise 50-word summary"
}
      ↓
Stack AI Output:
{
  "outputs": {
    "out-0": "{'image_url': 'https://...'}"
  }
}
      ↓
Frontend Display:
<img src="https://..." />
```

## Testing

### Test Script: `backend/test_stackai.py`

Run the test script to verify the integration:

```bash
cd backend
python3 test_stackai.py "Your scene description here"
```

**Features**:
- Tests API connectivity
- Validates response parsing
- Extracts and displays image URL
- Can test with custom descriptions

**Sample Output**:
```
✅ Extracted Image URL: https://oaidalleapiprodscus.blob.core.windows.net/...
```

### Manual Testing

1. **Start Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Test in Browser**:
   - Navigate to http://localhost:3000
   - Start a solo adventure
   - Submit a story action
   - Watch for:
     - Loading spinner appears in "Scene Visualization" section
     - Generated image displays after ~5-10 seconds
     - Image matches story content

## API Response Format Details

The Stack AI API returns images in this format:

```json
{
  "outputs": {
    "out-0": "{'image_url': 'https://oaidalleapiprodscus.blob.core.windows.net/private/...?st=...&se=...&sp=r&sv=...&sr=b&rscd=inline&rsct=image/png&...'}"
  },
  "citations": null,
  "run_id": "uuid-here",
  "metadata": null,
  "progress_data": null
}
```

**Key Points**:
- `outputs.out-0` contains a **string representation** of a Python dictionary
- Must parse using `ast.literal_eval()` (safer than `eval()`)
- Image URLs are Azure DALL-E blob storage URLs
- URLs include SAS tokens with expiration times
- URLs are temporary (typically 2 hours validity)

## Error Handling

### Backend
- Timeout set to 90 seconds (image generation can be slow)
- Comprehensive logging with `[Stack-AI]` prefix
- Returns `None` on failure (story continues without image)
- Catches and logs all exceptions

### Frontend
- Loading spinner during generation
- `onError` handler hides failed images
- Console logging for debugging
- Graceful degradation (story continues without image)

## Troubleshooting

### Image Not Displaying

1. **Check Backend Logs**:
   - Look for `[Stack-AI]` log messages
   - Verify API returns 200 status
   - Check if image URL was extracted

2. **Check Browser Console**:
   - Look for image load errors
   - Verify URL is valid
   - Check CORS issues

3. **Test API Directly**:
   ```bash
   cd backend
   python3 test_stackai.py "Test scene"
   ```

### Common Issues

**Issue**: Image URL extraction fails
- **Cause**: API response format changed
- **Solution**: Update parsing logic in `generate_scene_image()`

**Issue**: Images load slowly
- **Cause**: DALL-E generation takes time
- **Solution**: Normal behavior; loading spinner shown to user

**Issue**: Image URLs expire
- **Cause**: Azure SAS tokens have ~2 hour validity
- **Solution**: Images regenerated on new story progression

## Future Improvements

1. **Image Caching**: Store generated images to avoid regeneration
2. **Image History**: Display previous scene images in story timeline
3. **Style Customization**: Allow users to choose art styles
4. **Batch Generation**: Pre-generate images for predicted story paths
5. **Error Recovery**: Retry logic for failed image generation
6. **Progress Indicators**: Show generation progress percentage

## Configuration Options

### Environment Variables (Optional)

Create a `.env` file in the backend directory:

```env
STACK_AI_API_URL=your_api_url_here
STACK_AI_API_KEY=your_api_key_here
```

Then update `app.py` to load from environment:

```python
from dotenv import load_dotenv
load_dotenv()

STACK_AI_API_URL = os.getenv('STACK_AI_API_URL', 'default_url')
STACK_AI_API_KEY = os.getenv('STACK_AI_API_KEY', 'default_key')
```

## Summary

The Stack AI integration successfully adds visual scene generation to the D&D AI experience:

✅ **Backend**: Extracts summaries and calls Stack AI API  
✅ **Frontend**: Displays images with loading states  
✅ **Error Handling**: Graceful degradation on failures  
✅ **Testing**: Comprehensive test script provided  
✅ **Documentation**: Full integration details documented  

The integration enhances the storytelling experience by providing visual representations of the narrative scenes, making the adventure more immersive and engaging.

