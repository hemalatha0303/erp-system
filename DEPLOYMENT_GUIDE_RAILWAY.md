# Complete Deployment Guide: Local → Railway + Cloudflare Pages

**Project**: ERP System with AI (FastAPI Backend + MySQL + Static Frontend)  
**Total Cost**: ~$5-7/month (or nearly free with Railway's $5 free credit)  
**Deployment Time**: ~30-45 minutes

---

## Phase 1: Prepare Project Structure (Local, 10 minutes)

### Step 1.1: Create docker-compose.yml (if not exists)

```yaml
version: '3.8'

services:
  backend:
    build: ./Backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://root:password@mysql:3306/erp_db
      - JWT_SECRET=your-secret-key-here
    depends_on:
      - mysql
    volumes:
      - ./Backend:/app

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=erp_db
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### Step 1.2: Create .dockerignore in Backend folder

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
.git
.gitignore
.env.local
.env.*.local
*.log
.DS_Store
```

### Step 1.3: Create .env.example file

```
# Backend Configuration
DATABASE_URL=mysql+pymysql://root:password@mysql-host/erp_db
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com

# Password Reset
PASSWORD_RESET_BASE_URL=https://your-domain.com/reset-password.html

# Frontend URL (for CORS)
FRONTEND_URL=https://your-domain.com
```

### Step 1.4: Update Backend/app/core/config.py (Add validation)

Ensure this is at the top of config.py:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@127.0.0.1:3306/erp_db")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-default-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

# SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

if not JWT_SECRET or JWT_SECRET == "your-default-secret-key":
    import warnings
    warnings.warn("⚠️ JWT_SECRET not set! Using default value - NOT SECURE FOR PRODUCTION")
```

### Step 1.5: Update Backend/app/main.py (Add CORS)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ERP System", version="1.0.0")

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of your code
```

### Step 1.6: Create Frontend/.env file

```
VITE_API_URL=https://backend-railway-project.railway.app
VITE_APP_NAME=ERP System
```

---

## Phase 2: Push to GitHub (10 minutes)

### Step 2.1: Initialize Git Repository (if not already done)

```powershell
cd "c:\Users\hemal\Major Project Gallery\erp-deployment"
git init
git add .
git commit -m "Initial commit: ERP system with AI features"
```

### Step 2.2: Create .gitignore

```
# Environment
.env
.env.local
.env.*.local
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
env/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*.sublime-*

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Node
node_modules/
npm-debug.log
yarn-error.log

# Docker
.dockerignore

# Uploads
uploads/*
!uploads/.gitkeep

# Cache
.cache/
.pytest_cache/

# ML Models (optional - include or exclude based on size)
*.pkl
*.joblib
```

### Step 2.3: Create GitHub Repository

1. Go to https://github.com/new
2. Name: `erp-deployment`
3. Description: `Smart College ERP with AI-driven insights`
4. Make it **PUBLIC** (Railway needs access)
5. Click **Create Repository**

### Step 2.4: Push to GitHub

```powershell
git remote add origin https://github.com/YOUR_USERNAME/erp-deployment.git
git branch -M main
git push -u origin main
```

---

## Phase 3: Setup Railway (Backend + Database) (10 minutes)

### Step 3.1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub (recommended for easy integration)
3. Authorize Railway access to your GitHub account

### Step 3.2: Create New Project

1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Search and select `erp-deployment`
4. Click **"Deploy Now"**

### Step 3.3: Add MySQL Database

1. In Railway dashboard, click **"Add Service"** → **"Database"**
2. Select **"MySQL"**
3. Railway auto-creates MySQL instance with credentials

### Step 3.4: Configure Environment Variables

Railway dashboard → Click on **Backend Service** → **Variables tab**

Add these variables:
```
DATABASE_URL=mysql+pymysql://[USERNAME]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]
JWT_SECRET=your-super-secret-key-here-generate-a-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
CORS_ORIGINS=https://your-frontend-domain.pages.dev,https://your-custom-domain.com
FRONTEND_URL=https://your-frontend-domain
```

**To find MySQL credentials:**
- Click on **MySQL service** in Railway
- Go to **"Connect"** tab
- Copy credentials (Railway displays them automatically)

### Step 3.5: Configure Backend Startup

Railway dashboard → Backend Service → **"Deploy" tab**

For **Start Command**, use:
```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 3.6: Wait for Deployment

- Railway will build your Docker image automatically
- Takes ~3-5 minutes
- You'll see a **green checkmark** when ready
- Click on backend service to get the **publicly accessible URL**
  - Example: `https://backend-erp-production-123.railway.app`

### Step 3.7: Test Backend API

```powershell
# Test health endpoint
$backendUrl = "https://backend-erp-production-123.railway.app"
Invoke-WebRequest "$backendUrl/docs"  # Should return Swagger UI

# Or with curl
curl "https://backend-erp-production-123.railway.app/docs"
```

---

## Phase 4: Deploy Frontend to Cloudflare Pages (8 minutes)

### Step 4.1: Prepare Frontend for Static Hosting

Assuming your frontend uses index.html as entry point.

Create **FrontEnd/.nojekyll** file (empty):
```
# Just create empty file
```

### Step 4.2: Optional - Use Vite (Better for SPAs)

If you're using vanilla HTML/JS, consider adding Vite for better deployment:

```powershell
cd FrontEnd
npm install -D vite
```

Create **FrontEnd/vite.config.js**:
```javascript
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})
```

Update **FrontEnd/package.json** scripts:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### Step 4.3: Create Cloudflare Pages Project

1. Go to https://pages.cloudflare.com
2. Click **"Create a project"** → **"Connect to Git"**
3. Authorize Cloudflare to access GitHub
4. Select repository: `erp-deployment`
5. Configure build settings:
   - **Framework preset**: Vue (or select None for custom)
   - **Build command**: (leave empty or `npm run build` if using Vite)
   - **Build output directory**: `FrontEnd` (or `FrontEnd/dist` if using Vite)
   - **Root directory**: `/` (leave default)

### Step 4.4: Set Environment Variables (Cloudflare Pages)

1. Go to **Settings** → **Environment variables**
2. Add **Production** environment variables:
   ```
   VITE_API_URL=https://backend-erp-production-123.railway.app
   ```

### Step 4.5: Deploy

- Cloudflare automatically deploys on every push to GitHub
- Takes ~1-2 minutes
- You'll get a URL: `https://erp-deployment.pages.dev`

### Step 4.6: Update API URLs

Update all API calls in your frontend JavaScript files to use the environment variable:

In your JS files:
```javascript
// Instead of hardcoding
// const API_URL = "http://127.0.0.1:8000"

// Use environment variable
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

// Then use throughout
fetch(`${API_URL}/ai/aews/student-risk/22CSMA01`)
```

---

## Phase 5: Connect Custom Domain (Optional, 5 minutes)

### Option A: Use Cloudflare for Everything

1. **Transfer domain** to Cloudflare (or add nameservers)
2. In Cloudflare dashboard:
   - Go to **DNS** → Add Cloudflare nameservers to your domain registrar
   - Go to **Pages** → Your project → **Custom domains**
   - Add your domain: `erp.example.com`

### Option B: Use Domain Registrar Nameservers

1. In Cloudflare Pages → **Custom domains** → Add `erp.example.com`
2. Copy the CNAME record provided
3. Go to your domain registrar (GoDaddy, Namecheap, etc.)
4. Add CNAME record pointing to Pages

---

## Phase 6: Database Setup & Migrations (5 minutes)

### Step 6.1: Run Database Migrations on Railway

Railway has a "Shell" feature to run commands:

1. Click on **Backend service** in Railway
2. Go to **"Shell"** tab
3. Run:
   ```bash
   python alembic upgrade head  # If using Alembic
   # OR
   python create_tables.py  # If using your custom script
   ```

### Step 6.2: Verify Database Connection

```powershell
$backendUrl = "https://backend-erp-production-123.railway.app"
Invoke-WebRequest "$backendUrl/health"  # Should return 200 OK
```

---

## Phase 7: SSL/HTTPS Setup (Automatic)

✅ **Cloudflare Pages**: Automatic SSL certificate (free)  
✅ **Railway**: Automatic SSL certificate (free)  

No additional setup needed!

---

## Monitoring & Maintenance

### View Logs

**Railway Backend Logs:**
- Dashboard → Backend service → **"Logs"** tab
- Real-time logs + search functionality
- Download logs for debugging

**Cloudflare Pages Logs:**
- Pages project → **"Analytics"** tab
- Request metrics, status codes, errors

### Update Code

When you push changes to GitHub:
1. Railway automatically rebuilds backend (1-2 min)
2. Cloudflare automatically redeploys frontend (1 min)
3. No manual deployment needed!

### Monitor Costs

Railway:
- Backend: $7/mo (or free tier available)
- MySQL: $15/mo (or free tier available)
- Total: ~$5-22/month depending on usage

Cloudflare Pages: **FREE**

---

## Troubleshooting

### Backend shows 502 Bad Gateway

**Solution:**
1. Check Railway logs for errors
2. Verify DATABASE_URL is correct
3. Ensure JWT_SECRET is set
4. Restart service: Railway dashboard → **Restart deployment**

### Frontend can't connect to backend

**Solution:**
1. Verify CORS_ORIGINS includes your frontend domain
2. Check `VITE_API_URL` environment variable
3. Verify backend is running: Test `/docs` endpoint

### Database connection refused

**Solution:**
1. Copy exact credentials from Railway MySQL service
2. Verify DATABASE_URL format: `mysql+pymysql://user:pass@host:3306/db`
3. Check MySQL service is running in Railway

### CORS errors in browser console

**Solution:**
Add to CORS_ORIGINS in Backend environment variables:
```
https://erp-deployment.pages.dev
https://your-custom-domain.com
```

---

## Production Checklist

- [ ] Set strong JWT_SECRET (32+ characters)
- [ ] Configure real SMTP credentials for email
- [ ] Set up custom domain
- [ ] Update PASSWORD_RESET_BASE_URL
- [ ] Enable Railway database backups
- [ ] Set up monitoring/alerts
- [ ] Test all authentication flows
- [ ] Verify file upload paths
- [ ] Load test with realistic data
- [ ] Document API endpoints
- [ ] Create database backup

---

## Cost Breakdown

| Service | Component | Free Tier | Paid Price |
|---------|-----------|-----------|-----------|
| **Railway** | Backend CPU | Yes (limited) | $7/month |
| **Railway** | MySQL 5GB | Yes (limited) | $15/month |
| **Cloudflare Pages** | Frontend | **FREE** | $20+/month |
| **GitHub** | Repository | **FREE** | - |
| **Domain** | Custom domain | - | $10-15/year |
| **Total** | Per month | ~$0-5 | $32-37/month |

---

## Quick Reference Commands

```powershell
# Local testing
cd Backend
python -m uvicorn app.main:app --reload --port 8000

# Push changes to production
git add .
git commit -m "Your message"
git push origin main

# View Railway logs
railway logs --service backend

# SSH into Railway service (advanced)
railway connect backend
```

---

## Next Steps

1. ✅ Prepare project (Phase 1)
2. ✅ Push to GitHub (Phase 2)
3. ✅ Deploy Backend on Railway (Phase 3)
4. ✅ Deploy Frontend on Cloudflare Pages (Phase 4)
5. ✅ Configure custom domain (Phase 5)
6. ✅ Run database migrations (Phase 6)
7. ✅ Monitor logs and test (Phase 7)

**Estimated total time: 1-2 hours**

---

Made with ❤️ for ERP Deployment
