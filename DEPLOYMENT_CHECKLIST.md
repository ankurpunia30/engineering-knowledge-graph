# 🚀 Production Deployment Checklist

## Pre-Deployment Preparation

### ✅ Code Ready
- [x] All tests passing (60+ tests)
- [x] README.md complete and comprehensive
- [x] Dockerfile optimized for production
- [x] `.dockerignore` configured
- [x] `railway.json` configured
- [x] Requirements.txt up to date

### ✅ Docker Setup
- [x] Dockerfile created
- [x] Health check endpoint: `/health`
- [x] Port configuration: Uses `$PORT` env variable
- [x] Optimized image size with `.dockerignore`
- [x] Multi-stage build (optional enhancement)

### ✅ Environment Variables
Required for Railway:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Optional:
```bash
OPENAI_API_KEY=your_openai_key_here
NEO4J_URI=neo4j+s://your-neo4j-instance
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

---

## Railway Backend Deployment

### Step 1: Connect Repository
1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select `knowledgeGraph` repository

### Step 2: Configure Service
1. Railway auto-detects `Dockerfile` ✅
2. Build starts automatically
3. Wait for build to complete (~3-5 minutes)

### Step 3: Set Environment Variables
1. Click on your service
2. Go to **"Variables"** tab
3. Add **"New Variable"**:
   ```
   GROQ_API_KEY = gsk_...your_key...
   ```
4. Service will auto-restart

### Step 4: Get Public URL
1. Go to **"Settings"** tab
2. Click **"Generate Domain"**
3. Copy URL: `https://your-app.up.railway.app`
4. Test: `curl https://your-app.up.railway.app/health`

### Step 5: Verify Deployment
```bash
# Test health endpoint
curl https://your-app.up.railway.app/health

# Expected response:
# {"status": "healthy", "version": "3.0.0", "nodes": 21, "edges": 71}

# Test API docs
open https://your-app.up.railway.app/docs
```

---

## Vercel Frontend Deployment

### Step 1: Prepare Frontend
1. Update API URL in `frontend/src/services/api.js`:
   ```javascript
   const API_BASE = process.env.REACT_APP_API_URL || 
                     'https://your-app.up.railway.app';
   ```

2. Create `.env.production` in frontend/:
   ```
   REACT_APP_API_URL=https://your-app.up.railway.app
   ```

### Step 2: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import `knowledgeGraph` repository
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

5. Add Environment Variable:
   ```
   REACT_APP_API_URL = https://your-app.up.railway.app
   ```

6. Click **"Deploy"**

### Step 3: Update Backend CORS
Update `chat/app.py` to allow your Vercel domain:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add this
    "https://your-domain.com"       # Add custom domain if any
]
```

Redeploy backend after CORS update.

---

## Post-Deployment Testing

### Backend API Tests
```bash
export API_URL="https://your-app.up.railway.app"

# 1. Health check
curl $API_URL/health

# 2. Graph stats
curl $API_URL/api/graph/stats

# 3. Chat query
curl -X POST $API_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all services"}'

# 4. Upload file (test with small file)
curl -X POST $API_URL/api/upload \
  -F "file=@data/teams.yaml" \
  -F "file_type=teams"
```

### Frontend Tests
1. Open `https://your-app.vercel.app`
2. Verify graph loads
3. Test chat queries:
   - "Who owns payment-service?"
   - "What does order-service depend on?"
   - "What breaks if redis goes down?"
4. Test file upload
5. Test CRUD operations

---

## Performance Optimization

### Backend (Railway)
1. **Enable Compression**: Already enabled in FastAPI
2. **Add Caching**: 
   ```python
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.inmemory import InMemoryBackend
   
   @app.on_event("startup")
   async def startup():
       FastAPICache.init(InMemoryBackend())
   ```

3. **Database Connection Pooling**: If using Neo4j
4. **Rate Limiting**: Prevent abuse
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

### Frontend (Vercel)
1. **Already optimized**: Vercel automatically optimizes React builds
2. **CDN enabled**: Global edge network
3. **Image optimization**: Use Vercel Image component

---

## Monitoring Setup

### Railway Monitoring
1. **Built-in Metrics**:
   - Go to service > "Metrics" tab
   - View: CPU, Memory, Network, Requests

2. **Logs**:
   - Click "View Logs"
   - Filter by severity: Info, Warning, Error

3. **Alerts** (Railway Pro):
   - Set up uptime monitoring
   - Email/Slack notifications

### External Monitoring (Optional)
1. **UptimeRobot**: Free uptime monitoring
   - Add monitor: `https://your-app.up.railway.app/health`
   - Check interval: 5 minutes
   - Alert contacts: Your email

2. **Better Uptime**: More advanced monitoring
3. **DataDog**: Comprehensive APM (if needed)

---

## Cost Management

### Railway Costs
```
Free Tier:         $5 credit/month
Starter Plan:      $5/month + usage
Pro Plan:          $20/month + usage
```

**Estimated monthly costs:**
- **Development**: $0-5 (Free tier)
- **Production**: $5-15 (Small app)
- **High traffic**: $15-50+ (Scaling)

### Vercel Costs
```
Hobby:             $0 (Free, personal projects)
Pro:               $20/month (Commercial use)
```

**Recommendation**: Start with Railway Free + Vercel Hobby

---

## Backup & Disaster Recovery

### Data Backup
1. **Graph Data**:
   - Exported to JSON daily
   - Store in Railway volume or S3

2. **Configuration**:
   - All in Git repository ✅
   - Version controlled ✅

### Rollback Plan
If deployment fails:
```bash
# 1. Check Railway logs
# 2. Revert to previous deployment:
#    Railway > Deployments > Select previous > "Redeploy"

# 3. Local rollback:
git revert HEAD
git push origin main
```

---

## Security Checklist

- [x] API keys in environment variables (not in code)
- [x] HTTPS enabled by default (Railway provides SSL)
- [x] CORS configured properly
- [ ] Rate limiting implemented (optional)
- [ ] Authentication for sensitive endpoints (if needed)
- [ ] Input validation on all endpoints
- [ ] Regular dependency updates: `pip-audit`

---

## Documentation Updates

After deployment, update README.md with:
```markdown
## 🌐 Live Demo

- **API**: https://your-app.up.railway.app
- **Frontend**: https://your-app.vercel.app
- **API Docs**: https://your-app.up.railway.app/docs

## Quick Start (Production)

Try it out:
```bash
curl https://your-app.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all services"}'
```
```

---

## Troubleshooting Common Issues

### Issue: Build Fails on Railway
**Solution:**
- Check Dockerfile syntax
- Verify requirements.txt is valid
- Test build locally: `docker build -t ekg-test .`

### Issue: Application Crashes
**Solution:**
- Check Railway logs for errors
- Verify environment variables are set
- Ensure GROQ_API_KEY is valid

### Issue: Frontend Can't Connect
**Solution:**
- Verify CORS settings in `chat/app.py`
- Check API_URL in frontend env variables
- Test API directly: `curl $API_URL/health`

### Issue: High Memory Usage
**Solution:**
- Reduce graph size
- Implement pagination
- Use Neo4j instead of NetworkX for large graphs

---

## Success Metrics

Track these KPIs after deployment:
- ✅ Uptime: Target 99%+
- ✅ Response time: < 2s average
- ✅ Error rate: < 1%
- ✅ Daily active queries: Track growth
- ✅ User satisfaction: Gather feedback

---

## Final Checklist

### Backend (Railway)
- [ ] Deployed successfully
- [ ] Health check returns 200
- [ ] Environment variables configured
- [ ] Logs show no errors
- [ ] Public URL accessible
- [ ] API docs accessible at `/docs`

### Frontend (Vercel)
- [ ] Deployed successfully
- [ ] Connects to backend API
- [ ] Graph visualization works
- [ ] Chat queries work
- [ ] File upload works
- [ ] CRUD operations work

### Documentation
- [ ] README updated with live URLs
- [ ] RAILWAY_DEPLOYMENT.md reviewed
- [ ] API documentation complete
- [ ] Troubleshooting guide updated

### Testing
- [ ] All API endpoints tested
- [ ] Frontend fully functional
- [ ] Performance acceptable
- [ ] Mobile responsive (if applicable)

---

## 🎉 Deployment Complete!

Once all checks pass, you have a **production-ready Engineering Knowledge Graph** deployed to the cloud!

**Share your deployment:**
```
🚀 Engineering Knowledge Graph - LIVE!

📊 Backend API: https://your-app.up.railway.app
🎨 Frontend UI: https://your-app.vercel.app  
📖 API Docs: https://your-app.up.railway.app/docs

Built with: Python, FastAPI, React, Groq, Neo4j, NetworkX
Deployed on: Railway (backend) + Vercel (frontend)
```

**Next steps:**
1. Monitor logs for first 24 hours
2. Gather user feedback
3. Iterate based on usage patterns
4. Scale as needed

**Congrats! 🎊 You've deployed a production application!**
