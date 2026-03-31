# How to Set Environment Variables in Cloudflare Pages (Alternative Methods)

## Method 1: Via Deployment Settings
1. Pages Dashboard → Your Project
2. Top Menu: "Settings"
3. Left Sidebar: "Builds & deployments"
4. Scroll to "Environment variables"
5. Add: VITE_API_URL = https://erp-system-production-4ede.up.railway.app

## Backend CORS (Required)
Make sure your backend allows requests from your Cloudflare Pages domain.
Set this on the backend host (Railway/Render/etc):

```
CORS_ORIGINS=https://erp-system.hemalatha0303.workers.dev
```

If you use a workers.dev domain, include it too:
```
CORS_ORIGINS=https://erp-system.hemalatha0303.workers.dev
```

## Method 2: Via wrangler.toml (Advanced)
Create `wrangler.toml` in project root:
```toml
pages_build_output_dir = "FrontEnd"

[env.production]
vars = { VITE_API_URL = "https://erp-system-production-4ede.up.railway.app" }
```

## Method 3: Check Current Deployments
1. Pages Project → Deployments
2. Click latest deployment
3. Look for "Environment" section
4. Should show VITE_API_URL value

## Method 4: Via Cloudflare CLI
```bash
# Install wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy with env vars
wrangler pages deploy FrontEnd --project-name erp-deployment --env production
```

## Quick Fix: Hardcode in config.js (Temporary)
Edit `FrontEnd/config.js` and replace:
```javascript
return 'https://erp-system-production-4ede.up.railway.app';
```

## Verify It's Working
Open browser console (F12) and type:
```javascript
console.log(API_URL)
```
Should show your Railway URL
