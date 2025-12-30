# 🚀 Render Deployment Guide (100% FREE)

## Why Render?
- ✅ **100% FREE** - No credit card required
- ✅ **750 hours/month** - More than enough
- ✅ **Docker support** - Uses your Dockerfile
- ✅ **Auto-deploy** - From GitHub
- ✅ **Free SSL** - Automatic HTTPS

## 📋 Deployment Steps (10 minutes)

### Step 1: Sign Up
1. Go to: https://render.com
2. Click **"Get Started"**
3. Sign up with **GitHub** (easiest!)

### Step 2: Create Web Service
1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect GitHub"** (if not already connected)
4. Find and select: **`ankurpunia30/engineering-knowledge-graph`**
5. Click **"Connect"**

### Step 3: Configure Service
Fill in these settings:

**Basic Settings:**
- **Name:** `knowledge-graph` (or any name you like)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Runtime:** `Docker` ✅

**Instance Settings:**
- **Instance Type:** `Free` ✅

**Environment Variables:**
Click **"Add Environment Variable"** and add:
```
Key: GROQ_API_KEY
Value: your_groq_api_key_from_.env_file
```
(Use the value from your `.env` file)

### Step 4: Advanced Settings (Optional)
- **Auto-Deploy:** Yes (enabled by default)
- **Health Check Path:** `/health`

### Step 5: Deploy!
1. Click **"Create Web Service"**
2. Render will start building your Docker image
3. Wait **5-10 minutes** (first build takes longer)
4. Watch the logs for progress

### Step 6: Get Your URL
Once deployed, your URL will be:
```
https://knowledge-graph.onrender.com
```

---

## 🧪 Test Your Deployment

```bash
# Replace with your actual Render URL
export API_URL="https://knowledge-graph.onrender.com"

# Test health check
curl $API_URL/health

# Expected response:
{
  "status": "healthy",
  "nodes": 21,
  "edges": 71,
  "llm_provider": "groq",
  "storage_backend": "networkx"
}

# Open API docs
open $API_URL/docs

# Test chat
curl -X POST $API_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all services"}'
```

---

## ⚠️ Render Free Tier Limits

**What You Get:**
- ✅ 750 hours/month (31+ days!)
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ Free SSL/HTTPS
- ✅ Unlimited deployments

**Trade-off:**
- ⏸️ App **sleeps after 15 minutes** of inactivity
- 🔄 Takes **~30 seconds to wake up** on first request
- 💡 Good for demos and portfolios!

---

## 🔍 Monitor Your Deployment

### Check Logs:
1. Go to Render dashboard
2. Click on your service
3. Click **"Logs"** tab
4. Watch real-time logs

### Check Status:
- **Live** 🟢 - App is running
- **Building** 🟡 - Deploying
- **Failed** 🔴 - Check logs

---

## 🎯 What to Expect

### Build Logs:
```
==> Building Docker image
==> Installing dependencies
==> Starting application on port 10000
✅ INFO: Application startup complete
✅ INFO: Uvicorn running on http://0.0.0.0:10000
```

### First Request (after sleep):
```
⏸️ Service is spinning up (takes ~30 seconds)
```

### Subsequent Requests:
```
⚡ Fast response (app is awake!)
```

---

## 💡 Pro Tips

### Keep App Awake (Optional):
Use a free uptime monitor:
1. Go to: https://uptimerobot.com
2. Add monitor: `https://knowledge-graph.onrender.com/health`
3. Check every 5 minutes
4. Keeps your app awake during the day!

### Custom Domain (Optional):
1. Buy a domain from Namecheap/GoDaddy
2. Add CNAME record pointing to Render
3. Add custom domain in Render settings
4. Get free SSL automatically!

---

## 🆚 Comparison

| Feature | Render Free | Railway Trial | Vercel |
|---------|-------------|---------------|---------|
| **Cost** | $0 forever | $5 trial | Too large |
| **Credit Card** | Not required | Required | Not required |
| **Docker** | Yes ✅ | Yes ✅ | No ❌ |
| **Sleep** | Yes (15 min) | No | N/A |
| **Best For** | Your project! | Paid apps | Static sites |

---

## 🎉 Ready to Deploy!

**Go to:** https://render.com

**Sign up with GitHub and follow the steps above!**

Your app will be live in 10 minutes! 🚀

---

## 🆘 Troubleshooting

### Build Fails:
- Check Render logs for errors
- Make sure `Dockerfile` is in repo root
- Verify `requirements.txt` is complete

### App Won't Start:
- Check if `PORT` env variable is set correctly
- Render uses port `10000` by default
- Your start.sh script handles this automatically!

### 502 Bad Gateway:
- App is still starting (wait 1-2 minutes)
- Or app crashed (check logs)

---

**Deployment time: ~10 minutes**  
**Cost: $0/month forever**  
**Difficulty: Easy** ⭐⭐⭐⭐⭐

Let's get you deployed on Render! 🎊
