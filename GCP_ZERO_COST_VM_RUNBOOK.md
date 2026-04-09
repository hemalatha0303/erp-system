# GCP Zero-Cost VM Runbook

This is the safest deployment path for this project on a low-memory Google Cloud VM:

- Use one `e2-micro` VM in a free-tier eligible US region.
- Expose only port `80` publicly.
- Keep MySQL and FastAPI private inside Docker.
- Use Docker restart policies plus swap so the app survives small spikes.

## 1. Best Architecture

Public flow:

- Browser -> `http://VM_EXTERNAL_IP/`
- Nginx container on port `80`
- Nginx proxies `/api/*` -> backend container
- Backend talks to MySQL over Docker network

Do not use:

- `http://0.0.0.0:8000` in the browser
- Cloud Shell port forwarding for this VM-hosted app
- public MySQL port `3306`
- public backend port `8000`

## 2. GCP Choices That Keep Cost at Zero

- Machine type: `e2-micro`
- Region: `us-central1`, `us-east1`, or `us-west1`
- Disk: keep standard persistent disk at or below free-tier limits
- OS: Ubuntu LTS

## 3. Firewall Rules

Allow only:

- `tcp:80` from `0.0.0.0/0`
- `tcp:22` from your IP if using public SSH

Do not open:

- `tcp:3306`
- `tcp:8000`

If you use IAP SSH on a VM without a public IP, also allow TCP `22` from:

- `35.235.240.0/20`

## 4. VM Setup

SSH into the VM, then run:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and back in once so Docker works without `sudo`.

## 5. Add Swap

This is important on a 1 GB VM.

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

## 6. App Setup

In the VM:

```bash
git clone <your-repo-url> erp
cd erp
cp .env.example .env
```

Edit `.env` and set at least:

```env
MYSQL_ROOT_PASSWORD=strongpassword
MYSQL_DATABASE=erp_db
JWT_SECRET=replace-with-long-random-secret
FRONTEND_URL=http://YOUR_VM_EXTERNAL_IP
PASSWORD_RESET_BASE_URL=http://YOUR_VM_EXTERNAL_IP/reset-password.html
```

## 7. Start the App

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f backend
```

Expected result:

- `mysql` becomes healthy
- `backend` becomes healthy
- `frontend` starts and serves on port `80`

## 8. Health Checks

From inside the VM:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1/
```

From your laptop browser:

```text
http://YOUR_VM_EXTERNAL_IP/
```

## 9. Database Notes

Do not run table creation as the first fix anymore. The backend now waits for MySQL and creates tables on startup automatically.

Manual fallback only if needed:

```bash
docker compose exec backend python create_tables.py
```

Useful checks:

```bash
docker compose exec mysql mysql -uroot -p
SHOW DATABASES;
USE erp_db;
SHOW TABLES;
```

## 10. Stable Commands to Use

Good:

```bash
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 mysql
docker stats
free -h
df -h
```

Avoid on this VM:

```bash
docker compose exec backend bash
docker compose exec backend python create_tables.py
```

Use instead:

```bash
docker compose logs -f backend
docker compose exec backend python -u create_tables.py
```

## 11. If SSH Fails

Use this order:

1. Confirm the correct project is selected.
2. Confirm the VM has a running status.
3. Confirm firewall allows `22`.
4. If using IAP, confirm `35.235.240.0/20` is allowed on `22`.
5. Prefer Console browser SSH if local `gcloud` keys are broken.

Local CLI checks:

```bash
gcloud config get-value project
gcloud compute instances list
gcloud compute ssh VM_NAME --zone=ZONE
```

## 12. If the VM Feels Frozen

Check memory first:

```bash
free -h
docker stats --no-stream
```

If memory is exhausted:

- keep only one browser tab open for the app
- stop any unused containers
- avoid repeatedly rebuilding images
- avoid Cloud Shell port forwarding

## 13. Three-Day Demo Rules

For the next 3 days:

- do not redeploy unless needed
- do not open extra public ports
- do not run DB admin tools continuously
- do not use Cloud Shell preview for this VM app
- use `docker compose logs` for debugging instead of interactive shells
- snapshot the current `.env`

## 14. Recovery Commands

If the app stops responding:

```bash
docker compose ps
docker compose restart backend frontend
docker compose logs --tail=100 backend
docker compose logs --tail=100 mysql
```

If MySQL is corrupted or half-initialized during early testing:

```bash
docker compose down
docker volume ls
docker volume rm <project>_erp_mysql_data
docker compose up -d
```

Only do the volume reset if you are okay losing current DB data.
