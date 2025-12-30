# 🚂 Railway Deployment Guide (FIXED)

## ✅ Issue Fixed!

The `$PORT` variable was not being properly expanded in the Dockerfile. This has been fixed!

---

## 🚀 Railway Deployment Steps

### 1. **Your Project is Already Set Up!**
   - ✅ GitHub repo: `https://github.com/ankurpunia30/engineering-knowledge-graph`
   - ✅ Dockerfile fixed for Railway
   - ✅ railway.json configured
   - ✅ Code pushed to GitHub

### 2. **Railway Will Auto-Deploy**
   Since you've already connected your GitHub repo to Railway:
   - Railway detected the new push
   - It's rebuilding your container now
   - The new Dockerfile will properly use `$PORT`

### 3. **Add Environment Variable (if not done)**
   In Railway dashboard:
   1. Go to your project
   2. Click **"Variables"** tab
   3. Add:
      ```
      GROQ_API_KEY = your_groq_api_key_here
      ```
   4. Save

### 4. **Wait for Build to Complete**
   - Check the **"Deployments"** tab
   - Wait 3-5 minutes for build
   - Status will change to "Active" ✅

### 5. **Get Your URL**
   - Go to **"Settings"** → **"Networking"**
   - Your domain should be there
   - Or click **"Generate Domain"** if not set

### 6. **Test Your Deployment**
   ```bash
   # Replace with your Railway URL
   curl https://your-app-production.up.railway.app/health
   
   # Expected response:
   # {"status":"healthy","version":"3.0.0","nodes":21,"edges":71}
   ```

---

## 🐛 What Was Wrong?

### Before (Broken):
```dockerfile
CMD ["sh", "-c", "uvicorn chat.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
```
❌ The array syntax doesn't expand shell variables properly

### After (Fixed):
```dockerfile
ENV PORT=8000
CMD sh -c "uvicorn chat.app:app --host 0.0.0.0 --port $PORT"
```
✅ Removed array brackets, set default PORT, proper shell expansion

---

## 📊 Railway Free Tier

✅ **$5 credit/month** - Enough for your app!  
✅ **500 hours** execution time  
✅ **Unlimited projects**  
✅ **Auto-deploy** from GitHub  
✅ **Custom domains**  

**Your app should cost ~$2-3/month = stays in free tier!** 🎉

---

## 🔍 Monitor Your Deployment

### Check Logs:
1. Go to Railway dashboard
2. Click your project
3. Click **"Deployments"**
4. Click on the active deployment
5. View logs in real-time

### Check Metrics:
- CPU usage
- Memory usage
- Network traffic
- Request count

---

## ✅ Final Checklist

- [x] Dockerfile fixed for Railway
- [x] Code pushed to GitHub
- [ ] Railway auto-deploying now
- [ ] Add `GROQ_API_KEY` in Railway (if not done)
- [ ] Wait for build to complete
- [ ] Test `/health` endpoint
- [ ] Test `/docs` endpoint
- [ ] Test chat API

---

## 🎉 You're Almost Live!

Railway is now rebuilding your app with the fixed Dockerfile. 

**Check your Railway dashboard** to see the deployment progress!

Once it shows **"Active"**, test with:
```bash
curl https://your-app.up.railway.app/health
```

---

## 💡 Pro Tips

### Force Redeploy:
```bash
git commit --allow-empty -m "Force redeploy"
git push origin main
```

### View Logs:
Use Railway CLI (optional):
```bash
npm i -g @railway/cli
railway login
railway logs
```

### Set Custom Domain:
1. Go to Settings → Networking
2. Add your domain
3. Update DNS records
4. Get automatic HTTPS!

---

**Your app will be live in a few minutes! 🚀**
