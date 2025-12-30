# 🚀 Railway Deployment - Step-by-Step Guide

## What We Have Ready

✅ **Dockerfile** - Optimized for production  
✅ **railway.json** - Railway configuration  
✅ **.dockerignore** - Excludes unnecessary files  
✅ **Git Repository** - All code committed  
✅ **Health Check** - `/health` endpoint  
✅ **Port Configuration** - Uses `$PORT` environment variable

---

## Step 1: Create GitHub Repository (5 minutes)

Since you have a local Git repository, let's push it to GitHub:

```bash
# 1. Go to GitHub.com and create a new repository
# Name it: "knowledge-graph" or "engineering-knowledge-graph"
# Make it PUBLIC (free) or PRIVATE (if you have a paid plan)
# DO NOT initialize with README (we already have one)

# 2. Copy the repository URL (it will look like):
# https://github.com/YOUR_USERNAME/knowledge-graph.git

# 3. Add the remote and push:
cd /Users/ankur/knowledgeGraph
git remote add origin https://github.com/YOUR_USERNAME/knowledge-graph.git
git branch -M main
git push -u origin main
```

You'll need your GitHub username and a personal access token (not password).

### Get GitHub Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "Railway Deploy"
4. Check scope: `repo` (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)

---

## Step 2: Deploy Backend to Railway (10 minutes)

### 2.1 Sign Up for Railway
1. Go to: https://railway.app
2. Click "Start a New Project"
3. Sign in with GitHub (recommended)

### 2.2 Create New Project
1. Click **"+ New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub
4. Select your **`knowledge-graph`** repository

### 2.3 Railway Auto-Detects Everything! 🎉
Railway will:
- ✅ Detect your `Dockerfile`
- ✅ Read `railway.json` for configuration
- ✅ Start building the Docker image
- ✅ Deploy automatically

**Build takes ~3-5 minutes.** ⏰

### 2.4 Set Environment Variables
While it's building, add your API key:

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   ```
   Variable Name: GROQ_API_KEY
   Value: gsk_YOUR_KEY_HERE
   ```
5. Click "Add"

The service will automatically restart with the new variable.

### 2.5 Get Your API URL
1. Go to **"Settings"** tab
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. You'll get a URL like: `https://your-app-production.up.railway.app`

### 2.6 Test Your Deployment
```bash
# Replace with your actual URL
export API_URL="https://your-app-production.up.railway.app"

# Test health check
curl $API_URL/health

# Expected response:
# {"status":"healthy","version":"3.0.0","nodes":21,"edges":71}

# Test API docs
open $API_URL/docs
```

---

## Step 3: Deploy Frontend to Vercel (Optional, 10 minutes)

If you want a public UI:

### 3.1 Update Frontend API URL
Edit `frontend/src/services/api.js`:

```javascript
const API_BASE = process.env.REACT_APP_API_URL || 
                 'https://your-app-production.up.railway.app'; // Your Railway URL
```

Commit and push:
```bash
git add frontend/src/services/api.js
git commit -m "Update API URL for production"
git push
```

### 3.2 Deploy to Vercel
1. Go to: https://vercel.com
2. Sign in with GitHub
3. Click **"Add New..."** → **"Project"**
4. Import your **`knowledge-graph`** repository
5. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
6. Add Environment Variable:
   ```
   REACT_APP_API_URL = https://your-app-production.up.railway.app
   ```
7. Click **"Deploy"**

### 3.3 Update Backend CORS
Your Railway app needs to allow your Vercel domain.

Edit `chat/app.py`, find the CORS section and add your Vercel URL:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add this
]
```

Commit and push:
```bash
git add chat/app.py
git commit -m "Add Vercel domain to CORS"
git push
```

Railway will auto-deploy the update! 🚀

---

## Troubleshooting Common Issues

### Issue: Build Fails on Railway

**Check Build Logs:**
1. Go to your Railway project
2. Click on the service
3. Go to **"Deployments"** tab
4. Click on the failed deployment
5. Check the logs

**Common fixes:**
- Missing `requirements.txt`: Already in your repo ✅
- Python version mismatch: Dockerfile specifies Python 3.11 ✅
- Port configuration: Using `$PORT` variable ✅

### Issue: Application Crashes After Deployment

**Check Runtime Logs:**
1. In Railway, go to **"Deployments"**
2. Click on the active deployment
3. View runtime logs

**Common fixes:**
- Missing `GROQ_API_KEY`: Add it in Variables tab
- Database connection: You're using NetworkX (no DB needed) ✅
- Memory issues: Upgrade Railway plan if needed

### Issue: CORS Errors

**Solution:**
Update `chat/app.py` CORS settings to include your frontend domain:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend-domain.vercel.app",
    "*"  # Allow all (only for testing!)
]
```

---

## Cost Estimate

### Railway Pricing
```
✅ Free Tier:      $5 credit/month (good for development)
💰 Starter:        $5/month + usage
💼 Pro:            $20/month + usage
```

**Estimated Monthly Cost:**
- Small app (you): **$0-5** (Free tier covers it!)
- Medium traffic: **$5-15**
- High traffic: **$15-50**

### Vercel Pricing
```
✅ Hobby:          $0 (Free for personal projects)
💰 Pro:            $20/month (Commercial use)
```

**Recommendation:** Start with Railway Free + Vercel Hobby = **$0/month** 🎉

---

## Monitoring Your Deployment

### Railway Built-in Monitoring
1. Go to your service
2. Click **"Metrics"** tab
3. View:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

### Set Up Alerts (Railway Pro)
1. Go to **"Settings"** → **"Notifications"**
2. Add email or Slack webhook
3. Get notified of:
   - Deployment failures
   - High resource usage
   - Service crashes

### External Monitoring (Free)
**UptimeRobot** (recommended):
1. Go to: https://uptimerobot.com
2. Sign up for free account
3. Add monitor:
   - Type: HTTPS
   - URL: `https://your-app.up.railway.app/health`
   - Interval: 5 minutes
4. Add alert contact (email/SMS/Slack)

---

## Update README with Live URLs

After deployment, update your `README.md`:

```markdown
## 🌐 Live Demo

**Backend API:** https://your-app-production.up.railway.app  
**Frontend UI:** https://your-app.vercel.app _(if deployed)_  
**API Documentation:** https://your-app-production.up.railway.app/docs

## Quick Test

Try it out:
\`\`\`bash
curl https://your-app-production.up.railway.app/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "List all services"}'
\`\`\`
```

Commit and push:
```bash
git add README.md
git commit -m "Add live deployment URLs"
git push
```

---

## Deployment Checklist

Before submitting your assignment:

- [ ] GitHub repository is public (or share access with evaluator)
- [ ] Railway backend is deployed and accessible
- [ ] Health check returns `200 OK`: `/health`
- [ ] API docs are accessible: `/docs`
- [ ] Test chat query works
- [ ] README has live URLs
- [ ] GROQ_API_KEY is set in Railway
- [ ] All tests pass locally: `python tests/run_all_tests.py`
- [ ] Docker builds successfully
- [ ] (Optional) Frontend deployed to Vercel
- [ ] (Optional) Monitoring set up

---

## 🎉 Congratulations!

You now have a **production-ready Engineering Knowledge Graph** deployed to the cloud!

**What You Achieved:**
- ✅ Full-stack application deployed
- ✅ Docker containerized
- ✅ CI/CD with Git push
- ✅ Health monitoring
- ✅ Auto-scaling infrastructure
- ✅ Professional deployment

**Deployment URLs:**
```
Backend:  https://your-app.up.railway.app
Frontend: https://your-app.vercel.app
API Docs: https://your-app.up.railway.app/docs
```

**Share this in your assignment submission! 🚀**

---

## Need Help?

### Railway Support
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Common Commands
```bash
# Check Railway deployment logs
railway logs

# Force redeploy
git commit --allow-empty -m "Force redeploy"
git push

# View environment variables
railway variables

# Run command in Railway environment
railway run python main.py
```

---

**Built with ❤️ by Ankur**  
**Deployed on Railway + Vercel**  
**Powered by: Python, FastAPI, React, Groq, NetworkX**
