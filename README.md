# Enterprise Knowledge Graph (EKG) - Multi-Tenant Platform

A production-ready, multi-tenant Enterprise Knowledge Graph platform for visualizing and managing infrastructure dependencies across Docker Compose, Kubernetes, and Teams configurations with complete organization-level data isolation.

## 🎯 Overview

**Enterprise Knowledge Graph** helps organizations:
- 📊 **Visualize Infrastructure** - See all services, databases, APIs in one graph
- 🔍 **Track Dependencies** - Understand what depends on what (upstream/downstream)
- 💥 **Blast Radius Analysis** - Predict impact of changes before deployment
- 🏢 **Multi-Tenant Isolation** - Each organization's data is completely separate
- 🔒 **Production Security** - PostgreSQL authentication with JWT tokens

## ✨ Key Features

### Multi-Tenancy
- ✅ **100% Data Isolation** - Organizations cannot see each other's data
- ✅ **Organization Branding** - Dashboard shows your organization name
- ✅ **Team Management** - Multiple users per organization with role-based access
- ✅ **Usage Tracking** - See your organization's node/edge counts

### Authentication & Security
- ✅ **PostgreSQL Backend** - Production-grade database (with file-based fallback)
- ✅ **JWT Authentication** - Secure token-based API access
- ✅ **Bcrypt Password Hashing** - Industry-standard password security
- ✅ **Audit Logging** - Track all authentication events
- ✅ **Role-Based Access** - Admin, Member, Viewer roles

### Graph Features
- 📁 **Multi-Format Support** - Docker Compose, Kubernetes, Teams YAML
- 🔄 **Dependency Analysis** - Downstream (what you depend on) & Upstream (what depends on you)
- 💥 **Impact Analysis** - Blast radius calculation for change impact
- 🎨 **Interactive Visualization** - D3.js-powered graph explorer
- 🔍 **Advanced Queries** - Filter by type, team, environment

## 🚀 Quick Start (5 Minutes)

### 1. Start PostgreSQL
```bash
docker run -d --name ekg-postgres \
  -e POSTGRES_PASSWORD=ekg_secure_pass \
  -e POSTGRES_DB=ekg_auth \
  -p 5432:5432 postgres:15
```

### 2. Configure
```bash
export DATABASE_URL=postgresql://postgres:ekg_secure_pass@localhost:5432/ekg_auth
export SECRET_KEY=$(openssl rand -base64 32)
```

### 3. Initialize
```bash
pip install -r requirements.txt
python scripts/init_postgres_auth.py
python scripts/create_admin.py
```

### 4. Start
```bash
python main.py  # Backend on :8000
cd frontend && npm start  # Frontend on :3000
```

### 5. Test
```bash
python test_multi_tenancy.py
```

## 🧪 Verify Multi-Tenancy

```bash
python test_multi_tenancy.py
```

Expected: `✅ 🎉 MULTI-TENANCY TEST PASSED!`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register user/organization
- `POST /api/auth/login` - Login (returns JWT)
- `GET /api/auth/me` - Get current user

### Graph (Organization-Scoped)
- `GET /api/graph/data` - Get graph data
- `POST /api/upload` - Upload config file
- `GET /api/organization/info` - Org statistics
- `GET /api/query/downstream/{id}` - Dependencies
- `GET /api/query/upstream/{id}` - Dependents
- `GET /api/query/blast-radius/{id}` - Impact analysis

## 🔒 Multi-Tenancy

All data is automatically filtered by organization:

```python
# Every API call filters by user's organization_id
filtered_nodes = {k: v for k, v in nodes.items() 
                 if v.properties.get('organization_id') == current_user.organization_id}
```

Uploaded data is tagged:
```python
node.properties['organization_id'] = current_user.organization_id
node.properties['uploaded_by'] = current_user.email
node.properties['uploaded_at'] = datetime.now().isoformat()
```

## 🚀 Production Deployment

### PostgreSQL Options
- **AWS RDS** - $25-50/month (managed, backups)
- **DigitalOcean** - $15/month (simple)
- **Supabase** - Free tier available

### Backend Deployment
- **Railway** - Easiest, ~$5-20/month
- **DigitalOcean App Platform** - $12/month
- **AWS EC2** - $15-30/month (more control)

### Frontend Deployment
- **Vercel** - Free tier, auto-deploy
- **Netlify** - Free tier, simple
- **AWS S3 + CloudFront** - $1-5/month

### Required Environment Variables
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-minimum-32-characters
```

## 👥 User Management

### Register Organization
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "SecurePassword123!",
    "organization_name": "My Company",
    "role": "admin"
  }'
```

### Add Team Member
Use same `organization_name` to add to existing org.

### Roles
- **admin** - Full access, manage organization
- **member** - Upload and query data
- **viewer** - Read-only access

## 📤 Upload Data

### Via API
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d '{"email":"admin@company.com","password":"Pass"}' | jq -r '.access_token')

curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@docker-compose.yml" \
  -F "file_type=docker_compose"
```

### Supported Formats
- `docker_compose` - Docker Compose YAML
- `kubernetes` - Kubernetes YAML
- `teams` - Teams/microservices YAML

## 🔍 Query Examples

```bash
# Downstream dependencies
curl http://localhost:8000/api/query/downstream/my-service \
  -H "Authorization: Bearer $TOKEN"

# Upstream dependencies
curl http://localhost:8000/api/query/upstream/my-database \
  -H "Authorization: Bearer $TOKEN"

# Blast radius
curl http://localhost:8000/api/query/blast-radius/redis \
  -H "Authorization: Bearer $TOKEN"
```

## � Production Deployment

### Quick Deploy Options

#### Railway (Easiest - 15 min)
```bash
npm install -g @railway/cli
railway login
railway up
# Add PostgreSQL in dashboard
# Set: DATABASE_URL, SECRET_KEY
# Deploy frontend to Vercel: vercel
```

#### DigitalOcean (Simple - 20 min)
```bash
# Create PostgreSQL database in dashboard
# Deploy backend via App Platform (auto-detects Python)
# Deploy frontend via App Platform
# Set environment variables
```

#### AWS (Full Control - 1-2 hours)
```bash
# RDS PostgreSQL + EC2 backend
# S3 + CloudFront frontend
# nginx + Let's Encrypt SSL
```

### Post-Deployment
```bash
# Initialize database
python scripts/init_postgres_auth.py
python scripts/create_admin.py

# Test multi-tenancy
python test_multi_tenancy.py
```

## ⚡ Quick Commands

```bash
# Setup
docker run -d --name ekg-postgres -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=ekg_auth -p 5432:5432 postgres:15
export DATABASE_URL=postgresql://postgres:pass@localhost:5432/ekg_auth
export SECRET_KEY=$(openssl rand -base64 32)
pip install -r requirements.txt
python scripts/init_postgres_auth.py
python scripts/create_admin.py

# Run
python main.py                 # Backend :8000
cd frontend && npm start       # Frontend :3000

# Test
python test_multi_tenancy.py   # Multi-tenancy test
pytest tests/                  # Unit tests

# Database
psql $DATABASE_URL
SELECT COUNT(*) FROM organizations;
SELECT email, role FROM users;
```

## �🐛 Troubleshooting

### Backend falls back to file-based auth
```bash
pip install psycopg2-binary
export DATABASE_URL=postgresql://...
```

### Can't connect to database
```bash
pg_isready  # Check if PostgreSQL is running
psql $DATABASE_URL -c "SELECT 1;"  # Test connection
```

### Frontend doesn't show org bar
- Check browser console (F12)
- Verify token: `localStorage.getItem('token')`
- Ensure backend uses PostgreSQL (check logs)

## 📁 Project Structure

```
├── main.py                    # FastAPI entry
├── scripts/
│   ├── init_postgres_auth.py # DB initialization
│   └── create_admin.py       # Admin creation
├── test_multi_tenancy.py     # Isolation test
├── auth/                     # Authentication
├── chat/app.py               # Main API
├── graph/                    # Graph engine
├── connectors/               # File parsers
└── frontend/                 # React UI
```

## 📊 Database Schema

- **organizations** - Company/team data
- **users** - User accounts with org_id
- **refresh_tokens** - JWT refresh tokens
- **audit_logs** - Authentication events
- **password_reset_tokens** - Reset functionality
- **email_verification_tokens** - Email verification

## 📈 Roadmap

### Completed ✅
- Multi-tenancy with complete isolation
- PostgreSQL authentication
- Organization-aware UI
- JWT token security

### Short-term
- Organization management UI
- Email verification
- Usage quotas per plan
- Rate limiting

### Long-term
- Billing integration
- Analytics dashboard
- Webhook notifications
- Advanced RBAC

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📄 License

MIT License

## 🆘 Support

- **Issues**: GitHub Issues
- **Email**: support@yourcompany.com

---

**Built for Enterprise Infrastructure Teams** 🚀

Multi-tenant • Secure • Production-Ready
