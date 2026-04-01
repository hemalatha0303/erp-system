# CLOUD DEPLOYMENT GUIDE FOR SMART COLLEGE ERP SYSTEM

**Project:** FastAPI Backend + MySQL + Vanilla JS Frontend + ML Model  
**Options Analyzed:** Google Cloud Platform vs Microsoft Azure  
**Last Updated:** March 30, 2026

---

## EXECUTIVE SUMMARY

### Quick Recommendation Matrix

| Criteria | Google Cloud | Azure |
|----------|--------------|-------|
| **Ease of Use** | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Cost** | ⭐⭐⭐⭐ (Free credits) | ⭐⭐⭐ |
| **Python/ML Support** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Education Credits** | $300 credits | $200 credits |
| **Setup Time** | 30-45 min | 45-60 min |
| **Community Support** | Excellent | Good |

### **RECOMMENDATION: Google Cloud Platform** ✅

**Why GCP?**
1. **Better ML support** (your XGBoost/SHAP model)
2. **$300 free credits** (vs Azure's $200)
3. **Simpler setup** for Python projects
4. **AlloyDB** (better MySQL alternative)
5. **Vertex AI** integration if you scale ML

---

## PART 1: GOOGLE CLOUD DEPLOYMENT (RECOMMENDED)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   GOOGLE CLOUD                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Cloud Run    │  │ Cloud SQL    │  │ Cloud        │  │
│  │ (FastAPI)    │  │ (MySQL)      │  │ Storage      │  │
│  │ 500+ users   │  │ Automated    │  │ (Frontend    │  │
│  │ Auto-scale   │  │ Backup       │  │  + Models)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Cloud CDN    │  │ Firestore    │  │ Cloud        │  │
│  │ (Frontend)   │  │ (Notifications)  │ Tasks       │  │
│  │              │  │                  │ (Cron jobs) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Cloud Monitoring & Logging (Built-in)           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Step 1: Setup Google Cloud Project

#### 1.1 Create Project & Enable APIs

```bash
# Set project ID
PROJECT_ID="erp-college-system"

# Create project (via Console or gcloud)
gcloud projects create $PROJECT_ID --name="College ERP System"

# Set as default
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    run.googleapis.com \
    storage.googleapis.com \
    compute.googleapis.com \
    cloudresourcemanager.googleapis.com
```

#### 1.2 Create Service Account

```bash
# Create service account
gcloud iam service-accounts create erp-deployer \
    --display-name="ERP Deployment Service"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:erp-deployer@$PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/editor

# Create key
gcloud iam service-accounts keys create key.json \
    --iam-account=erp-deployer@$PROJECT_ID.iam.gserviceaccount.com

# Authenticate
gcloud auth activate-service-account --key-file=key.json
gcloud config set project $PROJECT_ID
```

---

### Step 2: Deploy Database (Cloud SQL)

#### 2.1 Create Cloud SQL Instance

```bash
# Create MySQL instance
gcloud sql instances create erp-mysql \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --backup-start-time=02:00 \
    --enable-bin-log

# Wait for instance creation (3-5 minutes)
gcloud sql instances describe erp-mysql

# Get instance connection name
gcloud sql instances describe erp-mysql --format='value(connectionName)'
# Output: PROJECT_ID:REGION:INSTANCE_NAME
```

#### 2.2 Create Database & User

```bash
# Create database
gcloud sql databases create erp_system --instance=erp-mysql

# Create root user
gcloud sql users create root --instance=erp-mysql --password=CHANGE_THIS_PASSWORD

# Get public IP
gcloud sql instances describe erp-mysql --format='value(ipAddresses[0].ipAddress)'
```

#### 2.3 Configure Cloud SQL Proxy (for local testing first)

```bash
# Download Cloud SQL Proxy
# Windows: https://dl.google.com/cloudsql/cloud_sql_proxy_x64.msi
# Linux: curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64

# Start proxy
./cloud_sql_proxy -instances=PROJECT_ID:us-central1:erp-mysql=tcp:3306

# In another terminal, test connection
mysql -h 127.0.0.1 -u root -p

# Should connect successfully
```

#### 2.4 Initialize Database Tables

```bash
# Copy your create_tables.py to cloud
# Update it to use cloud connection

# In Backend/:
# Edit Backend/create_tables.py to use proxy connection string

python create_tables.py
# This creates all 15+ tables in Cloud SQL
```

---

### Step 3: Prepare Backend for Cloud Run

#### 3.1 Create Dockerfile

Create `Backend/Dockerfile`:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 3.2 Update app/main.py for Cloud Run

```python
# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Update CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "YOUR_FRONTEND_DOMAIN.com",  # Add your domain
        "*"  # For development only - restrict in production
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3.3 Update .env for Cloud Run

Create `Backend/.env.gcp`:

```bash
# Database
MYSQL_HOST=/cloudsql/PROJECT_ID:us-central1:erp-mysql
MYSQL_USER=root
MYSQL_PASSWORD=SECURE_PASSWORD_HERE
MYSQL_DB=erp_system

# JWT
JWT_SECRET_KEY=generate-32-char-random-string-here
JWT_ALGORITHM=HS256

# APIs
GEMINI_API_KEY=your-gemini-api-key

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=app-password

# Environment
ENVIRONMENT=production
DEBUG=False
```

---

### Step 4: Deploy to Cloud Run

#### 4.1 Build Docker Image

```bash
# Navigate to Backend directory
cd Backend

# Configure Docker to use gcloud authentication
gcloud auth configure-docker gcr.io

# Build image
docker build -t gcr.io/$PROJECT_ID/erp-api:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/erp-api:latest

# Verify push
gcloud container images list
```

#### 4.2 Deploy to Cloud Run

```bash
# Deploy service
gcloud run deploy erp-api \
    --image gcr.io/$PROJECT_ID/erp-api:latest \
    --platform managed \
    --region us-central1 \
    --no-allow-unauthenticated \
    --set-env-vars-from-file=.env.gcp \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 100 \
    --min-instances 1

# Get service URL
gcloud run services describe erp-api --region us-central1 --format='value(status.url)'
```

#### 4.3 Configure Cloud SQL Connection

```bash
# Add Cloud SQL Client role to service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:erp-api@$PROJECT_ID.iam.gserviceaccount.com \
    --role=roles/cloudsql.client

# Update deployment with Cloud SQL proxy
gcloud run deploy erp-api \
    --image gcr.io/$PROJECT_ID/erp-api:latest \
    --add-cloudsql-instances PROJECT_ID:us-central1:erp-mysql \
    --set-env-vars CLOUDSQL_CONNECTION_NAME="PROJECT_ID:us-central1:erp-mysql"
```

---

### Step 5: Deploy Frontend to Cloud Storage + CDN

#### 5.1 Upload Frontend to Cloud Storage

```bash
# Create Cloud Storage bucket
gsutil mb gs://$PROJECT_ID-frontend

# Set CORS for frontend
cat > cors.json << EOF
[
  {
    "origin": ["*"],
    "method": ["GET","HEAD","DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://$PROJECT_ID-frontend

# Upload all frontend files
gsutil -m cp -r FrontEnd/* gs://$PROJECT_ID-frontend/

# Make files publicly readable
gsutil acl ch -u AllUsers:R gs://$PROJECT_ID-frontend/**
```

#### 5.2 Update Frontend API URL

Edit `FrontEnd/script.js`:

```javascript
// Update API base URL
const API_BASE_URL = 'https://erp-api-xxxxx-uc.a.run.app';

// Or use environment variable
const API_BASE_URL = process.env.REACT_APP_API_URL || 
                     'https://erp-api-xxxxx-uc.a.run.app';
```

#### 5.3 Setup Cloud CDN

```bash
# Create backend bucket
gcloud compute backend-buckets create erp-frontend-bucket \
    --gcs-uri-prefix=gs://$PROJECT_ID-frontend \
    --enable-cdn

# Create URL map
gcloud compute url-maps create erp-frontend \
    --default-service=erp-frontend-bucket

# Create HTTPS certificate (if custom domain)
gcloud compute ssl-certificates create erp-cert \
    --certificate=path/to/cert.pem \
    --private-key=path/to/key.pem

# Create frontend config
gcloud compute target-https-proxies create erp-frontend-proxy \
    --url-map=erp-frontend \
    --ssl-certificates=erp-cert
```

#### 5.4 Access Frontend

```
Frontend URL: https://storage.googleapis.com/$PROJECT_ID-frontend/index.html

Or with custom domain (if configured):
https://yourdomain.com/
```

---

### Step 6: Configure Monitoring & Logging

#### 6.1 Setup Cloud Logging

```bash
# View application logs
gcloud run services describe erp-api --format=json | jq '.status.url'

# Stream logs in real-time
gcloud run logs read erp-api --limit 50 --follow

# Filter logs
gcloud run logs read erp-api \
    --filter='severity:ERROR' \
    --limit 100
```

#### 6.2 Setup Monitoring

```bash
# Create uptime check
gcloud monitoring uptime create erp-api \
    --display-name="ERP API Health Check" \
    --resource-type=uptime-url \
    --monitored-resource-display-name=erp-api \
    --http-check-path=/health
```

---

### GCP DEPLOYMENT COST ESTIMATE

```
Monthly Costs (Estimated):

Cloud Run:
  - 500K requests/month: ~$2
  - 100 concurrent users: ~$15/month
  Subtotal: $17/month

Cloud SQL:
  - db-f1-micro instance: ~$8/month
  - Storage (10GB): ~$1.70/month
  - Backup storage: ~$1.70/month
  Subtotal: $11.40/month

Cloud Storage (Frontend):
  - 100MB storage: ~$2.40/month
  - Outbound traffic (100GB/month): ~$12/month
  Subtotal: $14.40/month

Cloud CDN:
  - Cache hits: ~$0.12/GB = ~$3/month
  Subtotal: $3/month

Monitoring & Logging:
  - Free tier covers most needs
  Subtotal: $0/month

================
TOTAL: ~$45.80/month

With $300 free credits: FREE FOR 6+ MONTHS ✅
```

---

## PART 2: AZURE DEPLOYMENT (ALTERNATIVE)

### Architecture Overview

```
┌─────────────────────────────────────────┐
│         MICROSOFT AZURE                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ App Service  │  │ Azure SQL    │    │
│  │ (FastAPI)    │  │ (MySQL)      │    │
│  └──────────────┘  └──────────────┘    │
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Static Web   │  │ Azure        │    │
│  │ Apps         │  │ CDN          │    │
│  │ (Frontend)   │  │              │    │
│  └──────────────┘  └──────────────┘    │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Application Insights (Monitoring)│  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### Step 1: Create Azure Account & Resource Group

```bash
# Login to Azure
az login

# Create resource group
az group create \
    --name erp-college-rg \
    --location eastus

# Set default group
az configure --defaults group=erp-college-rg

# List available locations
az account list-locations -o table
```

### Step 2: Deploy Azure SQL (MySQL)

```bash
# Create Azure SQL Server
az mysql server create \
    --resource-group erp-college-rg \
    --name erp-mysql-server \
    --location eastus \
    --admin-user sqladmin \
    --admin-password SECURE_PASSWORD_HERE \
    --sku-name B_Gen5_1 \
    --storage-size 51200 \
    --backup-retention 7 \
    --geo-redundant-backup Disabled

# Create database
az mysql db create \
    --resource-group erp-college-rg \
    --server-name erp-mysql-server \
    --name erp_system

# Get connection string
az mysql server show-connection-string \
    --server-name erp-mysql-server \
    --admin-user sqladmin
```

### Step 3: Setup Firewall Rules

```bash
# Allow local IP (for testing)
az mysql server firewall-rule create \
    --resource-group erp-college-rg \
    --server-name erp-mysql-server \
    --name AllowLocalIP \
    --start-ip-address YOUR_LOCAL_IP \
    --end-ip-address YOUR_LOCAL_IP

# Allow Azure services
az mysql server firewall-rule create \
    --resource-group erp-college-rg \
    --server-name erp-mysql-server \
    --name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

### Step 4: Deploy Backend to App Service

```bash
# Create App Service Plan
az appservice plan create \
    --name erp-api-plan \
    --resource-group erp-college-rg \
    --sku B1 \
    --is-linux

# Create App Service
az webapp create \
    --resource-group erp-college-rg \
    --plan erp-api-plan \
    --name erp-api-app \
    --runtime "PYTHON|3.11"

# Deploy from local repository
az webapp up \
    --name erp-api-app \
    --resource-group erp-college-rg \
    --runtime "PYTHON:3.11"
```

### Step 5: Configure Environment Variables

```bash
# Set app settings
az webapp config appsettings set \
    --resource-group erp-college-rg \
    --name erp-api-app \
    --settings \
    MYSQL_HOST=erp-mysql-server.mysql.database.azure.com \
    MYSQL_USER=sqladmin@erp-mysql-server \
    MYSQL_PASSWORD=SECURE_PASSWORD \
    MYSQL_DB=erp_system \
    JWT_SECRET_KEY=your-32-char-secret-here \
    GEMINI_API_KEY=your-api-key \
    ENVIRONMENT=production
```

### Step 6: Deploy Frontend to Static Web Apps

```bash
# Create Static Web App
az staticwebapp create \
    --name erp-frontend \
    --resource-group erp-college-rg \
    --source ./FrontEnd \
    --location eastus \
    --branch main

# Get deployment token
az staticwebapp deployment token list \
    --name erp-frontend \
    --resource-group erp-college-rg
```

### Azure Cost Estimate

```
Monthly Costs (Estimated):

App Service (B1):        ~$13.14/month
Azure SQL (B_Gen5_1):    ~$46/month
Static Web Apps:         Free (first 100GB)
CDN:                     ~$0.15/GB = ~$5/month
Monitoring:              ~$2/month

================
TOTAL: ~$66.14/month

With $200 free credits: FREE FOR 3+ MONTHS
```

---

## COMPARISON: GCP vs AZURE

| Feature | Google Cloud | Azure |
|---------|--------------|-------|
| **Setup Complexity** | ⭐⭐ Easy | ⭐⭐⭐ Moderate |
| **Python Support** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good |
| **Free Credits** | $300 (90 days) | $200 (12 months) |
| **Monthly Cost** | ~$45.80 | ~$66.14 |
| **ML Integration** | ⭐⭐⭐⭐⭐ (Vertex AI) | ⭐⭐⭐⭐ (ML Services) |
| **Auto-scaling** | Native in Cloud Run | Native in App Service |
| **Container Support** | Cloud Run | Azure Container Instances |
| **CLI Experience** | ⭐⭐⭐⭐⭐ (gcloud) | ⭐⭐⭐⭐ (az cli) |
| **Documentation** | Excellent | Excellent |
| **Community** | Large | Large |
| **Best For** | ML Projects | .NET/Windows Projects |

---

## RECOMMENDATION & NEXT STEPS

### ✅ RECOMMENDED: Google Cloud Platform

**Why GCP is better for this project:**

1. **Superior ML Support**
   - Your XGBoost model runs natively
   - SHAP explanations are faster
   - Vertex AI for future scaling

2. **Cost Efficient**
   - $300 credits (vs $200 on Azure)
   - Cheaper Cloud Run vs App Service
   - Better free tier coverage

3. **Simpler Setup**
   - Cloud Run auto-manages containers
   - No need for deployment slots
   - Built-in health checks

4. **Better Python Performance**
   - Cloud Run optimized for Python
   - faster cold start times
   - Better memory management

### Implementation Timeline

```
Day 1: Setup (2-3 hours)
  ├─ Create GCP project
  ├─ Enable APIs
  ├─ Create Cloud SQL instance
  └─ Configure initial setup

Day 2: Deployment (2-3 hours)
  ├─ Build Docker image
  ├─ Deploy to Cloud Run
  ├─ Configure database
  └─ Test endpoints

Day 3: Frontend & Monitoring (1-2 hours)
  ├─ Upload frontend to Cloud Storage
  ├─ Setup CDN
  ├─ Configure monitoring
  └─ Go live!

Total: 5-8 hours ✓
```

---

## QUICK START: GCP DEPLOYMENT (TL;DR)

```bash
# 1. Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# 2. Setup project
gcloud init
gcloud projects create erp-project --name="College ERP"
gcloud config set project erp-project

# 3. Enable APIs
gcloud services enable run.googleapis.com sqladmin.googleapis.com storage.googleapis.com

# 4. Create Cloud SQL
gcloud sql instances create erp-mysql --database-version=MYSQL_8_0 --tier=db-f1-micro

# 5. Build & Push Docker
cd Backend
docker build -t gcr.io/erp-project/api .
docker push gcr.io/erp-project/api

# 6. Deploy to Cloud Run
gcloud run deploy erp-api --image gcr.io/erp-project/api --platform managed

# 7. Upload Frontend
gsutil -m cp -r FrontEnd/* gs://erp-project-frontend/

# Done! 🎉
```

---

## POST-DEPLOYMENT CHECKLIST

- [ ] Application running on Cloud Run
- [ ] Database connected and populated
- [ ] Frontend accessible via Cloud Storage
- [ ] Health check endpoint responding
- [ ] ML model predictions working
- [ ] Logging and monitoring active
- [ ] CORS configured correctly
- [ ] SSL/TLS enabled
- [ ] Backup strategy in place
- [ ] Team given access credentials

---

## TROUBLESHOOTING

### Cloud Run App Won't Start

```bash
# Check logs
gcloud run logs read erp-api --limit 50

# Common issues:
# 1. Database connection timeout
#    - Verify Cloud SQL Proxy config
#    - Check firewall rules

# 2. Missing environment variables
#    - gcloud run deploy --set-env-vars XXXX

# 3. Out of memory
#    - Increase memory: --memory 1Gi
```

### Database Connection Issues

```bash
# Test connection locally
gcloud sql connect erp-mysql --user=root

# Check Cloud SQL Proxy
./cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE

# Verify service account permissions
gcloud projects get-iam-policy PROJECT_ID
```

---

**Ready to deploy? Start with GCP - it's the best fit for your project! 🚀**
