# Smart College ERP

College ERP with role-based portals (**Admin**, **HOD**, **Faculty**, **Student**), attendance, fees, hostel, library, timetables, notifications, and optional **AI-assisted** academic risk hints for faculty.

**Repository:** [github.com/hemalatha0303/erp-system](https://github.com/hemalatha0303/erp-system)

## Stack

| Layer | Technology |
|--------|------------|
| API | Python 3.11+, FastAPI, SQLAlchemy, JWT |
| Database | MySQL (PyMySQL) |
| Frontend | Static HTML / CSS / JavaScript (`FrontEnd/`) |
| Containers | Docker Compose: MySQL + API + nginx (static UI) |

## Repository layout

```
├── Backend/                 # FastAPI app (app/main.py)
│   ├── app/                 # Routers, models, services, schemas
│   ├── create_tables.py     # DB bootstrap helper
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example         # copy → .env for local API
├── FrontEnd/                # Admin, HOD, Faculty, Student UIs
├── docker/
│   └── Dockerfile.frontend  # nginx serving FrontEnd/
├── docker-compose.yml       # mysql + backend + frontend
└── .env.example             # optional root template
```

## Quick start (local)

1. **MySQL** — create database (e.g. `erp_db`).

2. **Backend**
   ```bash
   cd Backend
   python -m venv venv
   venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   copy .env.example .env        # set DATABASE_URL, JWT_SECRET
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend** — open `FrontEnd/index.html` via a local static server, or point browser at your hosted UI.  
   Ensure API calls use your backend base URL (many pages default to `http://127.0.0.1:8000`; change for deployment).

4. **Optional:** run `create_tables.py` once against the same `DATABASE_URL` if tables are not created automatically.

## Docker Compose

From the **repository root**:

```bash
docker compose build
docker compose up -d
```

- UI: `http://localhost:8080`  
- API docs: `http://localhost:8000/docs`  
- Override `JWT_SECRET` and DB credentials via environment or compose (do not commit secrets).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQLAlchemy URL, e.g. `mysql+pymysql://user:pass@host:3306/erp_db` |
| `JWT_SECRET` | Signing key for access tokens |
| SMTP / reset URL | Optional; see `Backend/app/core/config.py` and `.env.example` |

## Features (high level)

- Authentication and profiles; bulk user flows for admins  
- Attendance, internal/external marks, grades, semester results  
- Payments, fees, hostel, library  
- Timetable images; notifications and in-app alerts  
- Faculty student lookup, risk assessment UI (ML artifacts under `Backend/app/ml_models/` if present)

## Deployment notes

- For a **single VM** (e.g. GCP `e2-micro`), use root `docker-compose.yml`, open firewall ports **8080** (and **8000** if the UI calls the API directly), and set the frontend API base URL to your public host.  
- Database schema is defined by SQLAlchemy models; for production, use migrations or controlled DDL rather than ad-hoc scripts.

## License

Use and modify for your institution or academic project as appropriate.
