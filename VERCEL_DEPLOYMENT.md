# 🚀 Complete FREE Deployment on Vercel

Deploy both your **backend API** and **frontend UI** on Vercel for **$0/month**! 🎉

---

## 🎯 What You Get

✅ **FREE Hosting** - No credit card required  
✅ **Automatic HTTPS** - Secure by default  
✅ **Auto-Deploy** - Push to GitHub = instant deploy  
✅ **Global CDN** - Fast worldwide  
✅ **100GB Bandwidth/month** - Free tier  
✅ **Serverless Functions** - Python backend support  

---

## Prerequisites

✅ GitHub account  
✅ Your code already pushed to: `https://github.com/ankurpunia30/engineering-knowledge-graph`  
✅ GROQ API key  

---

## 🚀 Step 1: Deploy Backend API (5 minutes)

### 1.1 Go to Vercel
1. Open: https://vercel.com
2. Click **"Sign Up"** or **"Login"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your repositories

### 1.2 Import Your Project
1. Click **"Add New..."** → **"Project"**
2. Find **`engineering-knowledge-graph`** in the list
3. Click **"Import"**

### 1.3 Configure Backend Deployment
On the configuration page:

**Project Settings:**
- **Framework Preset**: Other
- **Root Directory**: `./` (leave as root)
- **Build Command**: Leave empty (we're using serverless)
- **Output Directory**: Leave empty

**Environment Variables** (CRITICAL!):
Click **"Environment Variables"** and add:
```
Name:  GROQ_API_KEY
Value: gsk_your_actual_groq_api_key_here
```

### 1.4 Deploy!
1. Click **"Deploy"**
2. Wait 2-3 minutes for deployment ⏱️
3. You'll get a URL like: `https://engineering-knowledge-graph.vercel.app`

### 1.5 Test Your Backend
```bash
# Replace with your actual Vercel URL
export API_URL="https://engineering-knowledge-graph.vercel.app"

# Test health check
curl $API_URL/health

# Expected response:
{"status":"healthy","version":"3.0.0","nodes":21,"edges":71}

# Open API docs
open $API_URL/docs
```

✅ **Backend is now live!**

---

## 🎨 Step 2: Deploy Frontend UI (5 minutes)

### 2.1 Update Frontend API URL
First, update your frontend to use the Vercel backend:

Edit `frontend/src/services/api.js`:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || 
                 'https://engineering-knowledge-graph.vercel.app/api';
```

Commit and push:
```bash
git add frontend/src/services/api.js
git commit -m "Update API URL for Vercel deployment"
git push origin main
```

### 2.2 Create Frontend Project on Vercel
1. Go back to: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import **`engineering-knowledge-graph`** AGAIN (yes, same repo!)

### 2.3 Configure Frontend Deployment
**Project Settings:**
- **Project Name**: `knowledge-graph-ui` (different from backend)
- **Framework Preset**: Create React App ✅
- **Root Directory**: `frontend` ⚠️ IMPORTANT
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

**Environment Variables:**
```
Name:  REACT_APP_API_URL
Value: https://engineering-knowledge-graph.vercel.app/api
```

### 2.4 Deploy!
1. Click **"Deploy"**
2. Wait 3-5 minutes (building React app) ⏱️
3. You'll get a URL like: `https://knowledge-graph-ui.vercel.app`

### 2.5 Update Backend CORS
Your backend needs to allow requests from your frontend domain.

Edit `chat/app.py` and find the CORS section (around line 70):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://knowledge-graph-ui.vercel.app",  # Add your frontend URL
        "*"  # Or use this to allow all (for testing)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push:
```bash
git add chat/app.py
git commit -m "Add Vercel frontend to CORS"
git push origin main
```

Vercel will **automatically redeploy** your backend! 🚀

---

## 🎉 You're Live!

### Your Live URLs:
```
🔗 Backend API:     https://engineering-knowledge-graph.vercel.app
🔗 Frontend UI:     https://knowledge-graph-ui.vercel.app
🔗 API Docs:        https://engineering-knowledge-graph.vercel.app/docs
🔗 GitHub:          https://github.com/ankurpunia30/engineering-knowledge-graph
```

### Test Everything:
```bash
# Test backend health
curl https://engineering-knowledge-graph.vercel.app/health

# Test chat API
curl -X POST https://engineering-knowledge-graph.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all services"}'

# Open UI in browser
open https://knowledge-graph-ui.vercel.app
```

---

## 📊 Vercel Free Tier Limits

✅ **Bandwidth:** 100 GB/month (plenty for your project!)  
✅ **Serverless Functions:** 100 GB-Hours/month  
✅ **Build Minutes:** 6,000 minutes/month  
✅ **Deployments:** Unlimited  
✅ **Team Members:** 1 (you)  
✅ **Domains:** Unlimited custom domains  

**Perfect for development and demos!** 🎯

---

## 🛠️ Troubleshooting

### Issue: Backend Returns 500 Error

**Solution:**
1. Go to: https://vercel.com/dashboard
2. Click on your backend project
3. Go to **"Deployments"** tab
4. Click on the latest deployment
5. Check **"Function Logs"** for errors

Common fixes:
- Missing `GROQ_API_KEY`: Add it in Project Settings → Environment Variables
- Import errors: Check that all dependencies are in `requirements.txt`

### Issue: Frontend Can't Connect to Backend

**Solution:**
1. Check CORS settings in `chat/app.py`
2. Make sure `allow_origins` includes your frontend URL
3. Verify `REACT_APP_API_URL` environment variable in frontend project

### Issue: "Module not found" Errors

**Solution:**
Make sure all dependencies are listed in `requirements.txt`:
```bash
# Check your requirements
cat requirements.txt

# Update if needed
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

---

## 🔄 Auto-Deployment Setup

Every time you push to GitHub, Vercel will automatically:
1. ✅ Pull the latest code
2. ✅ Run tests (if configured)
3. ✅ Build the project
4. ✅ Deploy to production
5. ✅ Send you a notification

**It's that easy!** 🚀

---

## 🌟 Pro Tips

### Custom Domain (Optional)
Add your own domain for free:
1. Go to Project Settings → Domains
2. Add your domain (e.g., `knowledgegraph.yourdomain.com`)
3. Update DNS records as instructed
4. Get automatic HTTPS!

### Preview Deployments
Every Pull Request gets its own preview URL:
- Create a branch: `git checkout -b feature-x`
- Make changes and push
- Vercel creates a preview URL automatically
- Test before merging!

### Environment Variables per Branch
Different settings for production vs. preview:
1. Go to Project Settings → Environment Variables
2. Select target: Production, Preview, or Development
3. Add different values for each environment

---

## 📈 Monitoring

### Vercel Analytics (Free)
1. Go to your project dashboard
2. Click **"Analytics"** tab
3. View:
   - Page views
   - Top pages
   - Unique visitors
   - Response times

### Function Logs
View real-time logs:
1. Go to project dashboard
2. Click **"Deployments"**
3. Click on any deployment
4. View **"Function Logs"**

---

## 💰 Cost Comparison

| Feature | Railway Free | Vercel Free | Winner |
|---------|-------------|-------------|--------|
| **Cost** | $5 credit/month | FREE forever | Vercel ✅ |
| **Bandwidth** | Limited | 100GB/month | Vercel ✅ |
| **Build Time** | 500 hours | 6000 minutes | Equal |
| **Domains** | 1 | Unlimited | Vercel ✅ |
| **Docker Support** | Yes ✅ | No | Railway |
| **Serverless** | No | Yes ✅ | Vercel |
| **Learning Curve** | Easy | Easy | Equal |

**For your project: Vercel wins! 🏆**

---

## 🎓 What You Achieved

✅ **Full-stack deployment** on Vercel  
✅ **Zero cost** - Completely free!  
✅ **CI/CD pipeline** - Auto-deploy on push  
✅ **Production-ready** - HTTPS, CDN, monitoring  
✅ **Professional URLs** - Share with anyone  
✅ **Scalable** - Handles traffic spikes automatically  

---

## 📝 Update Your README

Add these live URLs to your `README.md`:

```markdown
## 🌐 Live Demo

**🔗 Backend API:** https://engineering-knowledge-graph.vercel.app  
**🔗 Frontend UI:** https://knowledge-graph-ui.vercel.app  
**🔗 API Documentation:** https://engineering-knowledge-graph.vercel.app/docs  
**🔗 GitHub Repository:** https://github.com/ankurpunia30/engineering-knowledge-graph

### Quick Test
\`\`\`bash
# Test the live API
curl https://engineering-knowledge-graph.vercel.app/health

# Try a natural language query
curl -X POST https://engineering-knowledge-graph.vercel.app/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Show me all microservices"}'
\`\`\`
```

---

## 🎯 Final Checklist

Before submitting your assignment:

- [ ] Backend deployed to Vercel
- [ ] Frontend deployed to Vercel
- [ ] Health check works: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Test chat query successful
- [ ] CORS configured correctly
- [ ] GROQ_API_KEY set in Vercel
- [ ] README updated with live URLs
- [ ] GitHub repository is public
- [ ] All links work and are accessible

---

## 🆘 Need Help?

### Vercel Documentation
- Main Docs: https://vercel.com/docs
- Python on Vercel: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- Support: https://vercel.com/support

### Quick Commands
```bash
# Install Vercel CLI (optional)
npm i -g vercel

# Deploy from command line
vercel

# View logs
vercel logs

# List deployments
vercel ls
```

---

## 🎉 Congratulations!

You now have a **production-ready, fully deployed, completely FREE** Engineering Knowledge Graph!

**Share these URLs in your assignment submission:**
```
Backend:  https://engineering-knowledge-graph.vercel.app
Frontend: https://knowledge-graph-ui.vercel.app
GitHub:   https://github.com/ankurpunia30/engineering-knowledge-graph
```

**Built by:** Ankur Punia  
**Deployed on:** Vercel (FREE! 🎉)  
**Tech Stack:** Python, FastAPI, React, Groq, NetworkX  
**Cost:** $0/month  

---

**Happy Deploying! 🚀**
