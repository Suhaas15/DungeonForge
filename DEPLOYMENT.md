# 🚀 DungeonForge Deployment Guide

## Quick Deploy to Render

### Step 1: Commit and Push Your Code

```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Click "Get Started" and sign up with GitHub
3. Authorize Render to access your GitHub repositories

### Step 3: Deploy Backend (Flask API)

1. From Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `GauravHungund/DungeonForge-ContentHack2025-`
3. Configure the service:
   - **Name**: `dungeonforge-api`
   - **Region**: Oregon (US West) or closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python app.py`
   - **Instance Type**: Free

4. **Add Environment Variables** (click "Advanced"):
   ```
   PORT=10000
   FLASK_ENV=production
   FRONTEND_URL=https://your-frontend-url.onrender.com
   AIRIA_API_KEY=ak-MjEwNzg2MDc1MHwxNzYwNzMzNTgwMTAwfHRpLVUyRnVkR0ZEYkdGeVlWVnVhWFpsY25OcGRIazVMVTl3Wlc0Z1VtVm5hWE4wY21GMGFXOXVMVkJ5YjJabGMzTnBiMjVoYkE9PXwxfDM2NjE0OTAwNS
   ELEVENLABS_API_KEY=sk_dec58a061ba339d5b5549889cea277db008c6701b4625f12
   STACK_AI_API_URL=https://api.stack-ai.com/inference/v0/run/74329701-0f1c-429f-94f2-1a8bff522ae5/68f2b40560ba42fb86bdcc9b
   STACK_AI_API_KEY=2cca805e-ef0f-4c2c-990a-389db4d098d3
   ```

5. Click **"Create Web Service"**

6. **Copy the backend URL** (will be like: `https://dungeonforge-api.onrender.com`)

### Step 4: Deploy Frontend (React App)

1. From Render Dashboard, click **"New +"** → **"Static Site"**
2. Connect the same GitHub repository
3. Configure the service:
   - **Name**: `dungeonforge-frontend`
   - **Region**: Oregon (US West) or same as backend
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`

4. **Add Environment Variable**:
   ```
   REACT_APP_API_URL=https://dungeonforge-api.onrender.com
   ```
   ⚠️ Replace with YOUR actual backend URL from Step 3

5. Click **"Create Static Site"**

### Step 5: Update Backend CORS

1. Go back to your backend service on Render
2. Click **"Environment"** tab
3. Update `FRONTEND_URL` to your frontend URL (from Step 4)
   - Example: `https://dungeonforge-frontend.onrender.com`
4. Click **"Save Changes"**
5. The backend will automatically redeploy

### Step 6: Test Your App! 🎉

1. Visit your frontend URL: `https://dungeonforge-frontend.onrender.com`
2. Click "Single Player" or "Co-op Lobby"
3. Start your adventure!

---

## 📝 Important Notes

### Free Tier Limitations
- Services **spin down after 15 minutes** of inactivity
- First request after spin-down takes **~30 seconds** to wake up
- This is perfect for demos and hackathons!

### If Something Goes Wrong

1. **Check Logs**: 
   - Go to each service in Render Dashboard
   - Click "Logs" tab to see errors

2. **Common Issues**:
   - **CORS errors**: Make sure `FRONTEND_URL` matches your frontend URL
   - **API not found**: Check `REACT_APP_API_URL` in frontend environment
   - **Build fails**: Check that all dependencies are in `requirements.txt` and `package.json`

3. **Test endpoints**:
   ```bash
   # Test backend health
   curl https://your-backend-url.onrender.com/health
   
   # Should return: {"status": "ok"}
   ```

---

## 🔄 Updating Your Deployment

Every time you push to GitHub `main` branch:
- Render automatically redeploys your services
- Takes 2-5 minutes

To force a manual redeploy:
1. Go to your service in Render Dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

---

## 💰 Upgrading (Optional)

To avoid spin-down delays:
- Upgrade to **Starter Plan** ($7/month per service)
- Your app will stay awake 24/7
- Better for production use

---

## 🆘 Need Help?

1. Check Render documentation: https://render.com/docs
2. Look at the logs in Render Dashboard
3. Common errors are usually CORS or environment variable issues

---

**Your app should now be live! 🎮✨**

