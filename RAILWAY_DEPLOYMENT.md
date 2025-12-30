# 🚂 Railway Deployment Guide

This guide will help you deploy the Engineering Knowledge Graph to Railway.app.

---

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Groq API Key**: Get free API key from [console.groq.com](https://console.groq.com/)

---

## 🚀 Quick Deploy to Railway

### Option 1: One-Click Deploy (Recommended)

Click this button to deploy directly to Railway:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/YOUR_USERNAME/knowledgeGraph)

### Option 2: Manual Deployment

#### Step 1: Connect GitHub Repository

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `knowledgeGraph` repository
5. Click **"Deploy Now"**

#### Step 2: Configure Environment Variables

After deployment starts, go to your project settings:

1. Click on your service
2. Go to **"Variables"** tab
3. Add the following environment variables:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (Railway sets PORT automatically)
# PORT=8000  # Railway will override this

# Optional - for OpenAI fallback
# OPENAI_API_KEY=your_openai_key_here
```

#### Step 3: Verify Deployment

1. Railway will automatically:
   - Detect the `Dockerfile`
   - Build the Docker image
   - Deploy the container
   - Assign a public URL (e.g., `your-app.up.railway.app`)

2. Check the deployment logs:
   - Click on **"Deployments"** tab
   - View build and runtime logs
   - Look for: ✅ "Server started successfully"

3. Test the API:
   - Visit: `https://your-app.up.railway.app/health`
   - Should return: `{"status": "healthy", "version": "3.0.0"}`

4. Access API documentation:
   - Visit: `https://your-app.up.railway.app/docs`
   - Interactive Swagger UI

---

## 📁 Files Required for Railway

Your repository should have these files (already included):

```
knowledgeGraph/
├── Dockerfile              ✅ Railway uses this to build
├── railway.json           ✅ Railway configuration
├── .dockerignore          ✅ Optimizes Docker build
├── requirements.txt       ✅ Python dependencies
├── chat/app.py            ✅ FastAPI application
└── data/                  ✅ Config files
    ├── docker-compose.yml
    ├── teams.yaml
    └── k8s-deployments.yaml
```

---

## 🔧 Railway Configuration Details

### Dockerfile
```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Railway sets $PORT environment variable
CMD ["sh", "-c", "uvicorn chat.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### railway.json
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn chat.app:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

---

## 🌐 Frontend Deployment (Separate)

The React frontend should be deployed separately to Vercel or Netlify.

### Deploy Frontend to Vercel:

1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repository
4. Set **Root Directory** to: `frontend`
5. Add environment variable:
   ```
   REACT_APP_API_URL=https://your-railway-app.up.railway.app
   ```
6. Click **"Deploy"**

### Update Frontend API URL:

Edit `frontend/src/services/api.js`:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

---

## 🔍 Troubleshooting

### Build Fails

**Issue:** Docker build fails with dependency errors

**Solution:**
```bash
# Test locally first
docker build -t ekg-test .
docker run -p 8000:8000 -e GROQ_API_KEY="your_key" ekg-test
```

### Application Crashes on Startup

**Issue:** Application exits immediately after deployment

**Check:**
1. View Railway logs: Click "View Logs"
2. Verify environment variables are set
3. Check if `GROQ_API_KEY` is valid

**Solution:**
```bash
# Ensure requirements.txt includes all dependencies
pip freeze > requirements.txt

# Check for missing system dependencies in Dockerfile
```

### Port Binding Issues

**Issue:** Application doesn't respond

**Solution:**
- Railway automatically sets `$PORT` environment variable
- Application must listen on `0.0.0.0:$PORT`
- Already configured in Dockerfile

### CORS Errors

**Issue:** Frontend can't connect to backend

**Solution:**
Edit `chat/app.py` to include your frontend URL:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.vercel.app",  # Add this
]
```

### Data Persistence

**Issue:** Graph data resets on restart

**Solution:**
- Railway ephemeral filesystem resets on redeploy
- For persistence, use Railway's PostgreSQL or MongoDB addon
- Or use Neo4j Aura (cloud Neo4j database)

---

## 📊 Monitoring & Scaling

### View Metrics

1. Go to Railway dashboard
2. Click on your service
3. View:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Auto-Scaling

Railway automatically scales based on:
- Traffic volume
- Resource usage
- Health check status

### Custom Domain

1. Go to **"Settings"** tab
2. Click **"Domains"**
3. Add custom domain: `api.yourdomain.com`
4. Update DNS records as instructed

---

## 💰 Cost Estimation

Railway offers:
- **Free Tier**: $5 credit per month
  - Good for development/testing
  - ~550 hours of runtime
  
- **Starter Plan**: $5/month
  - More resources
  - Better for production

### Estimated Costs:
```
Backend (Railway):     $5-10/month
Frontend (Vercel):     $0 (free tier)
Total:                 $5-10/month
```

---

## 🔐 Security Best Practices

### 1. Use Environment Variables
Never hardcode API keys:
```python
# ✅ Good
api_key = os.getenv("GROQ_API_KEY")

# ❌ Bad
api_key = "gsk_abc123..."
```

### 2. Enable HTTPS
Railway provides HTTPS by default ✅

### 3. Configure CORS Properly
Only allow your frontend domain:
```python
allow_origins=[
    "https://your-frontend.vercel.app"
]
```

### 4. Add Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint():
    ...
```

---

## 🎯 Post-Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] Health check endpoint works: `/health`
- [ ] API documentation accessible: `/docs`
- [ ] Frontend can connect to backend
- [ ] Test all query types:
  - [ ] Ownership queries
  - [ ] Dependency queries
  - [ ] Blast radius queries
  - [ ] Path queries
- [ ] CORS configured for frontend domain
- [ ] Custom domain configured (optional)
- [ ] Monitoring enabled

---

## 📞 Support

### Railway Support
- Documentation: [docs.railway.app](https://docs.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)
- Twitter: [@Railway](https://twitter.com/Railway)

### Project Issues
- GitHub Issues: Create an issue in your repository
- Railway Logs: Check deployment logs for errors

---

## 🎉 Success!

Once deployed, your Engineering Knowledge Graph will be accessible at:
- **API**: `https://your-app.up.railway.app`
- **Docs**: `https://your-app.up.railway.app/docs`
- **Frontend**: `https://your-app.vercel.app`

**Share your deployment:**
```
🚀 Engineering Knowledge Graph
📊 API: https://your-app.up.railway.app
🎨 UI: https://your-app.vercel.app
📖 Docs: https://your-app.up.railway.app/docs
```

---

**Deployed! 🎊**
