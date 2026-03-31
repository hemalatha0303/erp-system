# 🚀 Quick Start Deployment Checklist (Railway + Cloudflare)

**⏱️ Time Required:** 45 minutes  
**💰 Cost:** FREE (first month) + ~$22/month after  
**📊 Difficulty:** Beginner-friendly

---

## Phase 0: Pre-Deployment (5 minutes)

- [ ] **Github Account** - Create one at https://github.com/join (free)
- [ ] **Railway Account** - Sign up at https://railway.app with GitHub
- [ ] **Cloudflare Account** - Create at https://dash.cloudflare.com (free)

---

## Phase 1: Prepare Local Project (8 minutes)

Navigate to your project folder in PowerShell:

```powershell
cd "c:\Users\hemal\Major Project Gallery\erp-deployment"
```

### Task 1.1: Create .env.example
Copy this and save as `Backend/.env.example`:
```
DATABASE_URL=mysql+pymysql://root:password@mysql-host/erp_db
JWT_SECRET=your-super-secret-key-here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
CORS_ORIGINS=http://localhost:3000,https://your-domain.pages.dev
FRONTEND_URL=http://localhost:3000
```

- [ ] `.env.example` created in Backend folder

### Task 1.2: Create .gitignore
Copy this and save as `.gitignore` in project root:
```
# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
venv/
env/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store

# Uploads
uploads/*
!uploads/.gitkeep

# Logs
*.log
```

- [ ] `.gitignore` created in project root

### Task 1.3: Check/Create Backend/app/main.py with CORS

Ensure your main.py has CORS:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ERP System")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] CORS middleware confirmed in main.py

---

## Phase 2: Push to GitHub (10 minutes)

```powershell
cd "c:\Users\hemal\Major Project Gallery\erp-deployment"

# Initialize Git
git init
git add .
git commit -m "Initial commit: ERP deployment ready"

# Go to https://github.com/new and create new repo named "erp-deployment"
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/erp-deployment.git
git branch -M main
git push -u origin main
```

**Expected output:**
```
Everything up-to-date
```

- [ ] Repository created on GitHub (https://github.com/YOUR_USERNAME/erp-deployment)
- [ ] Code pushed to GitHub main branch
- [ ] Repository is PUBLIC (Railway needs access)

**Verify:** Visit https://github.com/YOUR_USERNAME/erp-deployment in browser

---

## Phase 3: Deploy Backend on Railway (12 minutes)

### Task 3.1: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click **"+ New Project"** 
3. Select **"Deploy from GitHub repo"**
4. Search for and select **`erp-deployment`**
5. Click **"Deploy Now"** ✅

**⏳ Wait:** Railway builds Docker image (~3-5 minutes)

- [ ] Railway showing "Deployment Successful" ✅

### Task 3.2: Add MySQL Database

1. In Railway dashboard, click **"+ Add Service"**
2. Select **"Database"** → **"MySQL"**
3. Wait for MySQL to provision

- [ ] MySQL shows "✓ Ready"

### Task 3.3: Configure Environment Variables

1. Click on **Backend service** (your FastAPI app)
2. Go to **"Variables"** tab
3. Click **"RAW Editor"**
4. Paste this (replace with Railway's MySQL credentials shown on MySQL service page):

```
DATABASE_URL=mysql+pymysql://[USERNAME]:[PASSWORD]@[HOST]:3306/[DATABASE]
JWT_SECRET=generate-a-random-secret-key-at-least-32-characters-long-abc123xyz999
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
CORS_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000
```

**To find MySQL credentials:**
- Click on MySQL service in Railway
- Go to **"Connect"** tab
- You'll see: `mysql://username:password@host:port/database`

- [ ] Environment variables set
- [ ] DATABASE_URL correctly configured

### Task 3.4: Get Backend URL

1. Click on **Backend service**
2. Go to **"Deploy"** tab
3. Look for **URL** (like `https://erp-production-abc123.railway.app`)
4. Copy this URL **you'll need it in Phase 4**

- [ ] Backend URL copied: `https://erp-production-xxx.railway.app`

### Task 3.5: Test Backend

In your browser, visit:
```
https://your-backend-url/docs
```

Should see Swagger UI documentation ✅

- [ ] Backend accessible at `/docs` endpoint

---

## Phase 4: Deploy Frontend on Cloudflare Pages (10 minutes)

### Task 4.1: Create Cloudflare Pages Project

1. Go to https://pages.cloudflare.com
2. Click **"Create a project"** → **"Connect to Git"**
3. Authorize Cloudflare to access GitHub
4. Select **`erp-deployment`** repository
5. Configure build:
   - **Framework preset:** None (or leave blank)
   - **Build command:** (leave empty)
   - **Build output directory:** `FrontEnd`
   - **Root directory:** `/`
6. Click **"Save and Deploy"** ✅

**⏳ Wait:** Cloudflare deploys (~1-2 minutes)

- [ ] Cloudflare Pages deployment successful ✅
- [ ] Frontend URL provided (like `https://erp-deployment.pages.dev`)

### Task 4.2: Set Environment Variables

1. Go to Cloudflare Pages → Your project
2. Click **"Settings"** → **"Environment variables"**
3. Add for **Production** environment:
   ```
   VITE_API_URL = https://your-backend-url
   ```
   (Use your Railway backend URL from Phase 3)

4. Click **"Save"** ✅

- [ ] Environment variable `VITE_API_URL` set to Railway backend URL

### Task 4.3: Update Frontend Code

Find all JavaScript files in `FrontEnd/` and update API calls:

**Before:**
```javascript
const API_URL = "http://127.0.0.1:8000"
fetch(`${API_URL}/ai/aews/...`)
```

**After:**
```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
fetch(`${API_URL}/ai/aews/...`)
```

- [ ] All JS files updated to use environment variable
- [ ] Git push changes:
  ```powershell
  git add .
  git commit -m "Update API URLs to use environment variable"
  git push origin main
  ```

---

## Phase 5: Update Backend CORS (5 minutes)

1. Go back to Railway Backend service
2. Click **"Variables"** tab
3. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=http://localhost:3000,https://erp-deployment.pages.dev
   ```
4. Railway auto-redeployes ✅

- [ ] CORS_ORIGINS updated with frontend URL
- [ ] Backend redeployed (check "Deployment" tab)

---

## Phase 6: Run Database Migrations (3 minutes)

**If you have database setup scripts:**

1. In Railway dashboard, click Backend service
2. Go to **"Shell"** tab  
3. Run your database setup script:
   ```bash
   python create_tables.py
   ```

Or build DB schema any other way you have.

- [ ] Database tables created successfully

---

## ✅ Verification Checklist

Test your deployment:

### Backend Tests
- [ ] Visit `https://YOUR-BACKEND-URL/docs` → See Swagger UI
- [ ] Call a test endpoint (without authentication):
  ```powershell
  Invoke-WebRequest "https://YOUR-BACKEND-URL/ai/aews/test/student-risk/22CSMA01?semester=1"
  ```

### Frontend Tests
- [ ] Visit `https://erp-deployment.pages.dev` in browser
- [ ] Pages load (no 404 errors)
- [ ] Click to login
- [ ] Verify API calls work (check browser DevTools Console)

### Full Integration Test
- [ ] Login with your credentials
- [ ] Navigate to student pages
- [ ] Click "Check Risk" button (if AEWS is deployed)
- [ ] Modal shows data successfully

---

## 🎉 You're Live!

Your system is now deployed:

```
┌─ https://erp-deployment.pages.dev (Frontend)
│
├─→ API Calls ↓
│
└─ https://your-backend-url.railway.app (Backend + Database)
```

---

## 📝 Important Notes

### For Every Code Update:
```powershell
git add .
git commit -m "Description of changes"
git push origin main
```
- **Backend redeploys:** ~2-3 minutes (Railway watches GitHub)
- **Frontend redeploys:** ~1 minute (Cloudflare watches GitHub)

### Environment Variables Reference:

**Railway Backend Environment Variables:**
```
DATABASE_URL              → MySQL connection string
JWT_SECRET               → Your secret key for authentication
CORS_ORIGINS             → Frontendomain comma-separated  
SMTP_* (5 variables)      → Email configuration
```

**Cloudflare Environment Variables:**
```
VITE_API_URL             → Points to Railway backend
```

### Common Issues:

**Q: "Backend returns 502 Bad Gateway"**
- A: Check Railway logs. Verify DATABASE_URL is correct.

**Q: "Frontend can't reach backend"**
- A: Check CORS_ORIGINS includes your frontend domain
- A: Verify VITE_API_URL is correctly set in Cloudflare

**Q: "Database connection refused"**
- A: Copy exact credentials from Railway MySQL service
- A: Format must be: `mysql+pymysql://user:pass@host:3306/db`

---

## 🎓 Next Steps

After deployment:
1. Test all features thoroughly
2. Set up monitoring (Railway provides logs)
3. Plan database backups (Railway auto-backups included)
4. Create custom domain (if you want your own domain)
5. Set up monitoring alerts
6. Document API endpoints for team

---

## 💰 Cost Tracking

| Service | Component | Free (Month 1) | Paid (Month 2+) |
|---------|-----------|--|--|
| Railway | Backend | $5 credit | $7/month |
| Railway | Database | $5 credit | $15/month |
| Cloudflare | Frontend | FREE | FREE |
| Domain | Optional | - | ~$1/month |
| **TOTAL** | | **$0 (credit)** | **~$22/month** |

---

## Support & Resources

- **Railway Docs:** https://docs.railway.app
- **Cloudflare Pages:** https://developers.cloudflare.com/pages
- **FastAPI:** https://fastapi.tiangolo.com
- **Your detailed guide:** `DEPLOYMENT_GUIDE_RAILWAY.md`

---

**Good luck! Your ERP system is going to production! 🚀**
