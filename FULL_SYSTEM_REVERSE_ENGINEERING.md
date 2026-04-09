# Full System Reverse Engineering Report

## Scope and Ground Rules

This document reverse-engineers the repository at a source-code level.

It covers:

1. What the system does
2. Every authored folder and file in the repository
3. Backend and frontend runtime connections
4. Database entities and relationships
5. Request-response and user-flow traces
6. Deployment and environment wiring
7. Code review findings
8. Interview and presentation preparation

Important scope note:

- This report covers all project-authored files discovered with `rg --files`, excluding vendor/generated internals such as `.git`, `FrontEnd/node_modules/**`, and `__pycache__/**`.
- Those excluded folders are still acknowledged because they exist in the project tree and affect the development environment, but they are not business-logic source files written for this ERP system.

---

## Level 1: Full Project Understanding

### What exactly this project does

This project is a **college ERP system** with **role-based portals** for:

- `ADMIN`
- `HOD`
- `FACULTY`
- `STUDENT`

It centralizes the following functions:

- authentication and password reset
- student/faculty/HOD/admin profile management
- bulk admissions and bulk account creation from Excel
- academic record storage
- internal marks upload and editing
- external marks upload and result generation
- SGPA/CGPA computation
- attendance entry and attendance analytics
- fee structure management and transaction tracking
- hostel room management and student allocation
- library catalog upload, issue, return, and student library view
- timetable upload and timetable image delivery
- notifications and direct alerts
- AI-based academic risk prediction
- AI-based attendance advice

### Problem statement

Educational institutions often manage these workflows in separate spreadsheets or manual registers:

- admissions data
- student records
- marks records
- attendance registers
- fee ledgers
- hostel allotments
- library issue books
- notice circulation

That causes:

- duplicate data entry
- inconsistent records
- slow reporting
- role confusion
- delayed intervention for at-risk students

### Solution

This project solves that by building a single ERP-backed database with a role-specific interface:

- Admin manages the system-wide data and master operations
- HOD monitors departmental students and faculty
- Faculty records marks and attendance and monitors student risk
- Students view their own academic, fee, hostel, library, and notification data

The AI layer extends the ERP from record-keeping into early warning:

- it predicts student academic risk from attendance, mid marks, SGPA, and backlogs
- it explains risk with SHAP-based factor explanations
- it also generates short attendance advice using Gemini when attendance falls below the threshold

### Users

#### Admin

Primary responsibilities:

- upload student/faculty/HOD Excel sheets
- create fee structures
- upload external marks
- manage hostel rooms and allocations
- manage library inventory and returns
- view dashboard metrics
- send system-wide announcements

#### HOD

Primary responsibilities:

- maintain own profile
- view department faculty
- search student records
- view student analytics by batch/branch/section
- upload timetables
- send notifications and student alerts

#### Faculty

Primary responsibilities:

- maintain own profile
- view class students
- mark attendance
- upload/edit internal marks
- search student records
- check student academic risk
- send notifications and alerts

#### Student

Primary responsibilities:

- log in and view dashboard
- view profile
- view internal/external marks
- view attendance monthly and semester-wise
- view fee structure and transactions
- submit payment details
- view hostel allocation
- view library books
- view notifications and alerts
- view timetable

### Core workflows

1. User authentication and role-based redirection
2. Bulk data onboarding from Excel
3. Attendance capture and reporting
4. Internal marks recording and calculation
5. External marks upload and final result generation
6. Fees setup and transaction tracking
7. Hostel allocation lifecycle
8. Library issue-return lifecycle
9. Notification and alert delivery
10. Student risk analysis and intervention support

---

## Repository-Wide Architecture Summary

### Architecture type

This is a **layered monolithic web application**.

It is not microservices.

It follows this practical structure:

- static frontend layer
- FastAPI API layer
- service/business-logic layer
- SQLAlchemy persistence layer
- MySQL database layer
- optional ML inference layer

### Frontend style

The frontend is **multi-page static HTML/CSS/JavaScript**, not React, Vue, or Angular.

Each role has:

- HTML pages
- page-specific JavaScript
- page-specific CSS
- reusable header/sidebar components

### Backend style

The backend is a FastAPI application with these layers:

- `routers`: HTTP endpoint definitions
- `services`: business logic
- `models`: SQLAlchemy tables
- `schemas`: Pydantic request/response contracts
- `core`: config, DB session, JWT security
- `utils`: formula helpers and validation helpers

### Database style

The database is relational and centered around MySQL.

The schema is designed around:

- identity/authentication
- academic records
- operational modules

Important design characteristic:

- many connections are implemented with manual joins and key matching rather than SQLAlchemy `relationship()` declarations

### Deployment style

The intended deployment is containerized:

- MySQL container
- backend container
- nginx frontend container

with Docker Compose orchestrating them.

---

## Vendor and Generated Directories

These exist in the project tree but are not project-authored business logic.

### `.git/`

- What it is: Git metadata and version-control internals.
- Why needed: repository history, branches, refs, staging.
- If removed: the folder stops being a Git repository.
- Depends on: Git tooling.
- Used by: developer workflows only.

### `FrontEnd/node_modules/`

- What it is: installed frontend development dependency tree.
- Why needed: contains `prettier`, the only declared frontend dev dependency.
- If removed: formatting tool stops working until `npm install` is run again.
- Depends on: `FrontEnd/package.json` and `FrontEnd/package-lock.json`.
- Used by: developer tooling, not by runtime nginx serving.

### `__pycache__/`

- What it is: Python bytecode cache.
- Why needed: runtime optimization, auto-generated by Python.
- If removed: Python recreates it automatically.
- Depends on: imported Python modules.
- Used by: interpreter only.

### `uploads/`

- What it is: runtime-generated and runtime-served storage for timetable images.
- Why needed: HOD timetable upload stores faculty/class timetable PNGs here.
- If removed: uploaded timetable references break, and the UI will show no timetable until files are re-uploaded.
- Depends on: timetable upload flow.
- Used by: backend static mount and student/faculty timetable views.

---

## Level 2: Folder and File Deep Breakdown

## Root Folder

### Root folders

| Folder | What it is | Why it is needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `Academic_Early_Warning_System/` | ML training/prototype workspace | keeps notebook, raw data, processed data, and older inference prototype | training artifacts and research context are lost; deployed backend inference still works if `.pkl` files remain | Python ML stack | humans during ML experimentation |
| `Backend/` | FastAPI backend application | contains all API, DB, auth, business logic, ML inference integration | application backend stops existing | Python, FastAPI, SQLAlchemy, MySQL | all frontend pages and deployment |
| `docker/` | frontend container build context | contains nginx Dockerfile | Dockerized frontend build breaks | Docker | `docker-compose.yml` |
| `ExcelData/` | ignored local data directory | local helper folder for spreadsheet assets outside tracked source | no tracked source logic lost | none | local developer use |
| `FrontEnd/` | static browser UI | all role-based portals live here | users lose UI layer | browser, nginx | end users |
| `uploads/` | stored timetable images | runtime file serving for timetables | timetable viewing breaks | filesystem | backend static mount and UI |

### Root files

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `.env.example` | example environment file | shows required configuration shape | setup becomes harder and less consistent | none | developers |
| `.gitignore` | Git ignore rules | prevents secrets, caches, logs, and generated files from being committed | repo hygiene degrades | none | Git |
| `ARCHITECTURE_DIAGRAMS_15_FIGURES.md` | diagram documentation | presentation/report support | only documentation is lost | repo analysis | humans |
| `CLOUD_DEPLOYMENT_GUIDE.md` | deployment guide | explains GCP/Azure deployment strategy | deployment knowledge becomes less accessible | project structure assumptions | humans |
| `DATABASE_ARCHITECTURE.md` | ER-style DB documentation | communicates relational model | only docs lost | model understanding | humans |
| `docker-compose.yml` | multi-container orchestration file | starts MySQL, backend, frontend together | compose-based deployment breaks | Dockerfiles, images, env | Docker Compose |
| `MAJOR_PROJECT_REPORT.md` | academic project report | institutional/reporting artifact | only documentation lost | repo architecture narrative | humans |
| `README.md` | entry documentation | onboarding, stack summary, run instructions | new developers lose quick-start guide | repo layout | humans |
| `FULL_SYSTEM_REVERSE_ENGINEERING.md` | this analysis document | deep technical reverse engineering | only this report is lost | repository state | humans |

---

## Backend Folder Breakdown

## `Backend/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `Backend/requirements.txt` | Python dependency manifest | installs backend runtime libraries | backend environment cannot be reproduced cleanly | pip | Dockerfile, local setup |
| `Backend/Dockerfile` | backend container build file | packages FastAPI app into a container | backend container build fails | requirements, app code | Docker Compose |
| `Backend/create_tables.py` | schema bootstrap script | creates SQLAlchemy tables in DB without migrations | easier first-time setup is lost | models, DB engine | manual setup workflows |

### `Backend/app/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `Backend/app/__init__.py` | package marker | keeps package import-safe and side-effect free | package still may work in some contexts, but structure is less clean | none | Python imports |
| `Backend/app/main.py` | FastAPI entry point | builds the app, mounts uploads, configures CORS, registers routers | backend cannot start | routers, FastAPI, static files | uvicorn, Docker CMD |

## `Backend/app/core/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `core/__init__.py` | duplicate/legacy security helper module | package marker plus old duplicated security code | little direct runtime impact; mostly dead/legacy code | jose, passlib, config | not meaningfully used |
| `core/config.py` | environment config loader | central place for DB URL, JWT, SMTP, reset URL | config becomes scattered and imports fail | `python-dotenv`, `os` | DB, auth, email, AI services |
| `core/database.py` | SQLAlchemy engine/session/base | central DB connection and session factory | DB access breaks across app | SQLAlchemy, config | models, routers, services |
| `core/dependencies.py` | auth dependency module | decodes bearer token for protected routes | role checks and authenticated endpoints break | FastAPI security, jose, config | routers |
| `core/security.py` | password hashing + JWT creation | handles password hashing/verification and JWT signing | login/signup/password change break | passlib, jose, config | auth service, bulk user service |

## `Backend/app/models/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `models/admin.py` | `admin_profiles` table | stores admin profile metadata | admin profile endpoints lose persistence | SQLAlchemy base | admin service/router |
| `models/academic.py` | `academics` table | stores per-student academic enrollment state | student academic views and many joins break | SQLAlchemy base | student/admin/faculty/HOD/payment/hostel flows |
| `models/alert.py` | `alerts` table | stores direct student alert messages | faculty/HOD alert workflow breaks | SQLAlchemy base | faculty/HOD/student alert views |
| `models/attendance_record.py` | child attendance rows | stores one student’s status in one attendance session | attendance analytics break | session FK, base | attendance service |
| `models/attendance_session.py` | attendance session header | groups one subject/date/period attendance event | attendance record grouping breaks | base | attendance service |
| `models/course_grade.py` | `course_grades` + `semester_grades` tables | stores derived subject grades and semester GPA/CGPA | result computation and transcript views break | base, student FK | external marks service, student grades router |
| `models/external_marks.py` | semester exam marks table | stores uploaded external exam marks | final results pipeline breaks | student FK, base | admin upload, result viewing |
| `models/faculty.py` | faculty profile table | stores faculty profile and subject/branch assignment | faculty views break | base | faculty/HOD/admin flows |
| `models/fee_structure.py` | fee structure master table | stores fee amounts by quota/residence/year | fee computation becomes impossible | base | admin/payment/hostel services |
| `models/hod.py` | HOD profile table | stores HOD profile | HOD profile flows break | base | HOD service/router |
| `models/hostel_allocation.py` | hostel allocation table | links student to room with status lifecycle | hostel module breaks | student FK, room FK | hostel service |
| `models/hostel_room.py` | hostel room master table | stores room capacity and occupancy | hostel room CRUD breaks | base | hostel service/admin UI |
| `models/internal_marks.py` | internal marks table | stores raw internal components and derived mid totals | faculty marks module breaks | student FK, base | internal marks services, dashboard AI features |
| `models/library_books.py` | library catalog table | stores book metadata and copy counts | library catalog breaks | base | library service/router |
| `models/library_issue.py` | issue/return transaction table | tracks student-book borrow lifecycle | student/admin library module breaks | book FK, base | library service/router |
| `models/notification.py` | notification inbox table | stores role/batch/branch/section targeted messages | notification system breaks | base | notification service, role routers |
| `models/payment.py` | fee transaction table | stores each payment transaction | fee tracking and receipts break | base | payment service/router, dashboards |
| `models/semester_result.py` | legacy result table | older result storage model kept for backward compatibility | little current impact; legacy integrations may break | base | rarely used directly |
| `models/student.py` | student profile table | stores student personal + some academic identity fields | most ERP workflows fail | base | almost every business module |
| `models/subject.py` | subject master table | subject metadata storage | not heavily used in current runtime but useful for normalization | base | potential academic extensions |
| `models/timetable.py` | timetable image metadata table | links uploaded timetable images to class/faculty context | timetable module breaks | base | student/faculty/HOD timetable flows |
| `models/user.py` | authentication identity table | login credential source and role authority | auth breaks system-wide | base | auth service, all protected routes |

## `Backend/app/schemas/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `schemas/academic.py` | academic response schema | typed output for academic records | one API loses structured response model | Pydantic | academic router |
| `schemas/admin.py` | admin profile schemas | typed admin profile update/response | admin profile validation breaks | Pydantic | admin router |
| `schemas/alert.py` | alert payload schemas | typed alert creation/response | alert endpoint validation weakens/breaks | Pydantic | faculty/HOD routers |
| `schemas/attendance.py` | attendance mark request schema | validates faculty attendance payload | attendance marking becomes fragile | Pydantic | faculty router |
| `schemas/auth.py` | auth request/response schemas | validates login/signup/reset payloads | auth endpoint contracts break | Pydantic | auth router |
| `schemas/bulk_upload.py` | bulk upload response schema | typed credential response helper | minor typing loss | Pydantic | admin account tooling |
| `schemas/excel_upload.py` | Excel upload response schema | simple upload message schema | minor typing loss | Pydantic | upload flows |
| `schemas/external_marks.py` | external marks schema | legacy typed payload for marks | minor direct impact; not central to runtime | Pydantic | potential/legacy use |
| `schemas/faculty.py` | faculty profile schemas | validates and serializes faculty profile data | faculty profile endpoints break | Pydantic | faculty router |
| `schemas/fee_structure.py` | fee structure schemas | validates fee master creation | fee admin flows break | Pydantic | admin router |
| `schemas/hod.py` | HOD profile schemas | validates HOD profile update/response | HOD profile flows break | Pydantic | HOD router |
| `schemas/hostel.py` | hostel request schemas | validates hostel CRUD/allocation payloads | hostel admin endpoints break | Pydantic | admin router |
| `schemas/internal_marks.py` | internal marks fetch/update schemas | validates marks editing fetch/update | marks module breaks | Pydantic | faculty router |
| `schemas/library.py` | library issue/return schemas | validates library transaction payloads | library admin actions break | Pydantic | library router |
| `schemas/notification.py` | notification schemas | validates notification target/category/priority payloads | notification module breaks | Pydantic | admin/faculty/HOD routers |
| `schemas/payment.py` | payment schemas | validates payment lookup/update/submit payloads | fee module becomes fragile | Pydantic | payment router, student router |
| `schemas/student.py` | student profile schemas | validates student profile update and response | student profile endpoints break | Pydantic | student router |
| `schemas/timetable.py` | timetable schemas | legacy structured timetable schema definitions | small direct impact; image-based flow still exists | Pydantic | potential future expansion |

## `Backend/app/services/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `services/academic_service.py` | bulk academic record insert logic | supports academic-record persistence from extracted rows | Excel academic insert flow breaks | models | academic-related uploads |
| `services/admin_service.py` | admin profile logic | encapsulates admin profile read/update | admin profile router becomes fatter or breaks | admin model | admin router |
| `services/ai_service.py` | Gemini attendance advice integration | turns low-attendance data into short AI guidance | `/ai/student/attendance/ai-advice` loses generative advice | `requests`, env, Gemini API | AI router, student dashboard fallback flows |
| `services/attendance_service.py` | attendance business logic | creates sessions/records and computes analytics | attendance module breaks | attendance/student models, SQL functions | faculty and student routers |
| `services/auth_service.py` | auth business logic | signup/login/password reset token flow | auth router loses logic | user model, security, validators, email | auth router |
| `services/bulk_user_service.py` | bulk account creation logic | creates many user identities from Excel with generated passwords | admin account generation breaks | user/faculty/HOD models, security | admin accounts router |
| `services/email_service.py` | SMTP mail delivery | sends password reset emails | reset email flow fails | SMTP config | auth service |
| `services/excel_marks_service.py` | core marks upload pipeline | parses internal/external marks Excel files and computes grades | marks upload and result pipeline break | openpyxl, models, formulas | faculty/admin routers |
| `services/excel_service.py` | admissions/profile Excel import pipeline | imports students/faculty/HOD and initial payment records | admissions bulk upload breaks | openpyxl, models, security | admin router |
| `services/external_marks_service.py` | result serialization logic | provides backward-compatible external/result payload | old student results UI breaks | external marks, course grade, semester grade | student router |
| `services/faculty_service.py` | faculty profile + student lookup logic | keeps faculty router thinner | faculty profile/student lookup flow breaks | faculty/student/academic models | faculty/HOD routers |
| `services/fee_compliance_service.py` | payment compliance analytics | summarizes paid/partial/unpaid by batch/year | fee analytics extensions break | academic/student/fee/payment models | future analytics |
| `services/fee_structure_service.py` | fee master create/bulk-create logic | centralizes fee-structure persistence rules | admin fee setup breaks | fee structure model | admin router |
| `services/hod_service.py` | HOD profile logic | encapsulates HOD profile operations | HOD profile router breaks | HOD model | HOD router |
| `services/hostel_service.py` | hostel room/allocation business logic | handles upload, allocate, vacate, stats, CRUD | hostel module breaks | hostel/student/academic/payment models | admin and student routers |
| `services/inference.py` | deployed ML inference layer | loads model artifacts and returns risk text/JSON | academic risk feature disappears | joblib, pandas, shap, model files | student dashboard, AI router |
| `services/internal_marks_service.py` | internal marks fetch/update logic | supports faculty marks editing and student internal view | internal marks page breaks | internal marks/student models, formulas | faculty and student routers |
| `services/library_service.py` | library business logic | upload catalog, issue, return, student view | library module breaks | library/student/academic models | library router, student dashboard |
| `services/notification_service.py` | notification persistence and filtering | centralizes targeting rules by role/batch/branch/section/email | notifications break | notification model, SQL conditions | admin/faculty/HOD/student routers |
| `services/payment_service.py` | fee computation and transaction handling | core fee structure vs payment reconciliation and receipt creation | fee module breaks | student/academic/payment/fee models | payment router, student router |
| `services/student_service.py` | student profile logic | profile upsert helper | student profile update breaks | student model | student router |
| `services/timetable_service.py` | timetable file upload logic | writes timetable images and DB metadata | timetable upload breaks | filesystem, timetable model | HOD router |

## `Backend/app/routers/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `routers/__init__.py` | legacy duplicate student-grade router | package file plus old duplicate endpoints | little runtime impact because `main.py` uses `student_grades.py` instead | FastAPI, models | largely unused |
| `routers/academic.py` | academic endpoints | exposes `/academic/my` | academic API path breaks | DB/session/auth/schema | frontend/student flows |
| `routers/admin.py` | admin domain endpoints | major admin module surface | admin operations disappear | services, models, schemas, auth | admin UI |
| `routers/admin_accounts.py` | bulk account endpoints | supports admin credential generation from Excel | user management screen breaks | excel reader, bulk user service | admin UI |
| `routers/ai_route.py` | AI endpoints | exposes attendance advice and risk assessment | AI API disappears | inference/attendance/AI services | faculty/student UI |
| `routers/auth.py` | auth endpoints | login/signup/change/reset password surface | no authentication | auth service, schemas | login/reset UI |
| `routers/faculty.py` | faculty endpoints | faculty profile, attendance, marks, notifications, alerts | faculty portal breaks | services, models, auth | faculty UI |
| `routers/hod.py` | HOD endpoints | profile, faculty lookup, student analytics, timetable, notifications, alerts | HOD portal breaks | services, models, auth | HOD UI |
| `routers/library.py` | library endpoints | catalog, upload, issue, return, pending, student books | library UI breaks | library service/schemas | admin/student UI |
| `routers/payment.py` | payment endpoints | admin payment views and payment update | fee admin UI breaks | payment service/schemas | admin fee UI |
| `routers/student.py` | main student endpoints | dashboard, profile, attendance, fees, hostel, timetable, notifications | student portal core breaks | services/models/auth | student UI |
| `routers/student_grades.py` | student grade endpoints | transcript and detailed semester results | richer academic APIs disappear | grade models, formulas | student academic UI |

## `Backend/app/utils/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `utils/academic_year.py` | year resolver helper | derives study year from batch/semester when callers omit year | many routes would duplicate logic or behave inconsistently | `datetime` | marks, attendance, Excel flows |
| `utils/excel_reader.py` | Excel extraction helper | parses input spreadsheets into normalized row dictionaries | admin upload/account routes become messier | openpyxl | admin routes/services |
| `utils/marks_calculator.py` | grading/math helper | central formulas for mid, internal, SGPA, CGPA, grade conversion | marks logic duplicates and drifts | none | marks services, dashboards |
| `utils/validators.py` | email validators | central format/domain checks | auth/notification validation weakens | none | auth, faculty/admin/HOD notification flows |

## `Backend/app/ml_models/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `ml_models/academic_risk_model.pkl` | trained classifier artifact | core prediction engine for student risk | risk prediction becomes unavailable | ML training pipeline | inference service |
| `ml_models/model_features.pkl` | feature-order artifact | ensures runtime input matches training feature order | predictions become wrong or fail | ML training pipeline | inference service |
| `ml_models/scaler.pkl` | fitted scaler artifact | applies same normalization as training time | predictions become inconsistent or fail | ML training pipeline | inference service |

---

## FrontEnd Folder Breakdown

## `FrontEnd/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `FrontEnd/index.html` | login page | entry point for all users | users lose browser entry page | `style.css`, `script.js` | browser |
| `FrontEnd/script.js` | login/reset page logic | handles login, change password, forgot/reset password, API base rewrite | login and reset interactions break | DOM, auth API | `index.html` |
| `FrontEnd/style.css` | global login page styling | makes login and shell pages usable and branded | login UI still works but becomes unstyled | HTML class names | `index.html`, some child pages via shared root CSS |
| `FrontEnd/reset-password.html` | standalone reset password page | alternate dedicated reset UI | standalone flow disappears; integrated reset in `index.html` still exists | inline CSS/JS, auth API | password reset link if configured |
| `FrontEnd/package.json` | frontend npm manifest | declares `prettier` dev dependency | frontend formatting tool setup breaks | npm | developers |
| `FrontEnd/package-lock.json` | dependency lockfile | deterministic install for frontend tooling | installs may drift | npm | developers |
| `FrontEnd/id_samples.json` | sample generated credentials data | reference/sample for admin user generation outputs | only sample data lost | none | humans |
| `FrontEnd/fees.json` | sample bulk fee structure payload | reference input for fee structure setup | only sample data lost | none | humans |

## `FrontEnd/admin/`

### Admin components

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `admin/components/header.html` | static admin top bar | reusable admin header fragment | header area becomes blank on admin pages | CSS classes | `admin/js/main.js` + admin HTML pages |
| `admin/components/sidebar.html` | admin navigation menu | reusable navigation for admin pages | navigation disappears | page URLs, CSS, logout handler | `admin/js/main.js` + admin HTML pages |

### Admin HTML pages

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `admin/html/dashboard.html` | admin dashboard page | shows summary stats and recent activity | admin landing view disappears | root CSS, admin CSS, `admin/js/dashboard.js`, shared components | admin users |
| `admin/html/admissions.html` | admissions bulk upload page | uploads student/faculty/HOD Excel sheets | Excel onboarding screen disappears | `admin/js/admissions.js`, admissions CSS, shared components | admin |
| `admin/html/students.html` | record browser page | lists students/faculty/HOD and shows modal details | record management screen disappears | `admin/js/students.js`, students CSS | admin |
| `admin/html/fees.html` | fee management page | creates fee structure and manages payments/receipts | fee admin UI disappears | `admin/js/fees.js`, fees CSS | admin |
| `admin/html/hostel.html` | hostel management page | room upload, room CRUD, allocation lifecycle | hostel admin UI disappears | `admin/js/hostel-new.js`, hostel CSS | admin |
| `admin/html/library.html` | library admin page | upload books, issue, return, catalog search | library admin UI disappears | `admin/js/library.js`, library CSS | admin |
| `admin/html/users.html` | bulk user creation page | creates login accounts from Excel and downloads credentials | user provisioning UI disappears | `admin/js/users.js`, users CSS | admin |
| `admin/html/results.html` | external marks upload page | uploads semester external marks Excel files | result publication UI disappears | `admin/js/results.js`, admissions CSS reuse | admin |
| `admin/html/notifications.html` | announcement page | sends notifications to roles/batches | admin announcement UI disappears | `admin/js/notifications.js`, dashboard CSS reuse | admin |

### Admin JavaScript

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `admin/js/main.js` | shared admin shell logic | loads header/sidebar, rewrites API base, handles logout and nav highlighting | admin pages lose shared shell behavior | browser fetch, DOM, components | all admin HTML pages |
| `admin/js/dashboard.js` | dashboard logic | fetches `/admin/dashboard/stats` and `/admin/dashboard/activity` | dashboard stays static/loading | admin API | `dashboard.html` |
| `admin/js/admissions.js` | admissions upload logic | renders expected Excel format and uploads bulk profile sheets | admissions page becomes informational only | DOM, `/admin/upload-students` | `admissions.html` |
| `admin/js/students.js` | record table logic | switches among student/faculty/HOD datasets, fetches lists, shows detail modal | records page breaks | `/admin/students`, `/admin/faculty`, `/admin/hods` | `students.html` |
| `admin/js/fees.js` | fee workflow logic | creates fee structures, looks up payment history, prints receipts, records payments | fees page breaks | admin/payment APIs, DOM | `fees.html` |
| `admin/js/hostel.js` | older hostel script | legacy simple room upload/allocate/vacate logic | little current impact because page uses `hostel-new.js` | older hostel endpoints | legacy/unused |
| `admin/js/hostel-new.js` | current hostel management logic | full room CRUD, stats, allocation status, UI tabs | hostel management page breaks | hostel admin APIs | `hostel.html` |
| `admin/js/library.js` | library admin workflow logic | catalog fetch, upload, issue, return, pending book lookup | library admin page breaks | library APIs | `library.html` |
| `admin/js/users.js` | bulk credential generation logic | uploads account sheet, renders credentials, downloads CSV | user management page breaks | `/admin/accounts/signup-users` | `users.html` |
| `admin/js/results.js` | result upload logic | uploads external marks Excel by batch/semester/branch/section | results page breaks | `/admin/external-marks/upload/...` | `results.html` |
| `admin/js/notifications.js` | admin notification logic | sends announcements with category/priority and optional batch targeting | notification page breaks | `/admin/notifications` | `notifications.html` |

### Admin CSS

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `admin/css/components.css` | shared admin shell styling | styles sidebar/header/common layout | admin shell becomes visually broken | component markup | all admin pages |
| `admin/css/dashboard.css` | dashboard/notification shared styling | stats cards, tables, form cards | dashboard-like pages become unstyled | dashboard page classes | dashboard and notifications |
| `admin/css/admissions.css` | admissions/results styling | upload area and admissions forms | admissions/results layout degrades | admissions/results markup | admissions, results |
| `admin/css/students.css` | record browser styling | tables, filters, details modal | records page becomes hard to read | students page markup | students |
| `admin/css/fees.css` | fee page styling | tables, modal, payment sections | fees page loses usability | fees markup | fees |
| `admin/css/hostel.css` | older hostel styling | legacy hostel page support | legacy styles disappear | old hostel markup | older hostel approach |
| `admin/css/hostel-new.css` | current hostel styling | tabs, stats cards, modals, allocation tables | hostel page usability degrades | current hostel markup | hostel |
| `admin/css/library.css` | library styling | issue/return/catalog layout | library page becomes unstyled | library markup | library |
| `admin/css/users.css` | user management styling | upload area, credentials results table | users page loses structure | users markup | users |

## `FrontEnd/faculty/`

### Faculty components

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `faculty/components/header.html` | faculty top bar fragment | reusable page shell | header disappears | CSS classes | `faculty/js/main.js` |
| `faculty/components/sidebar.html` | faculty nav fragment | reusable faculty navigation | page navigation disappears | page URLs, CSS | `faculty/js/main.js` |

### Faculty HTML pages

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `faculty/html/dashboard.html` | faculty landing page | profile summary + timetable card | faculty home screen disappears | dashboard/faculty CSS, `faculty/js/dashboard.js` | faculty |
| `faculty/html/profile.html` | faculty profile page | shows own profile details | faculty profile screen disappears | `faculty/js/profile.js` | faculty |
| `faculty/html/attendance.html` | attendance entry page | class attendance marking workflow | attendance UI disappears | `faculty/js/attendance.js` | faculty |
| `faculty/html/marks.html` | marks entry page | internal marks fetch/edit/upload | marks UI disappears | `faculty/js/marks.js` | faculty |
| `faculty/html/students.html` | student lookup and risk page | search/filter students, send alerts, run risk checks | faculty advisory UI disappears | `faculty/js/students.js` | faculty |
| `faculty/html/notifications.html` | send/inbox notifications page | faculty notices to students + inbox | faculty notification UI disappears | `faculty/js/notifications.js` | faculty |

### Faculty JavaScript

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `faculty/js/main.js` | shared faculty shell logic | loads components, rewrites API base, nav highlighting, logout | faculty shell breaks | DOM, components | all faculty pages |
| `faculty/js/dashboard.js` | dashboard data loader | fetches faculty profile and timetable | dashboard remains empty | faculty APIs | `dashboard.html` |
| `faculty/js/profile.js` | faculty profile loader | fills profile fields from API | profile page stays blank | `/faculty/get-profile` | `profile.html` |
| `faculty/js/faculty.js` | alternate dashboard logic | loads faculty dashboard profile and timetable; overlaps dashboard.js | some page variants may break | faculty APIs | certain faculty page layouts |
| `faculty/js/attendance.js` | attendance workflow | fetches students in class and submits attendance payload | attendance entry breaks | `/faculty/class-students`, `/faculty/attendance/mark` | `attendance.html` |
| `faculty/js/marks.js` | marks workflow | fetches class students, loads existing marks, edits or uploads Excel | marks module breaks | internal marks APIs | `marks.html` |
| `faculty/js/students.js` | student advisory workflow | fetches student list, computes fee status, risk checks, sends notifications/alerts | student monitoring page breaks | faculty APIs, AI APIs | `students.html` |
| `faculty/js/notifications.js` | faculty notice send/inbox logic | sends filtered student notifications and renders inbox | notification page breaks | `/faculty/notifications` | `notifications.html` |

### Faculty CSS

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `faculty/css/components.css` | shared faculty shell styling | header/sidebar/common components | faculty shell loses structure | component markup | all faculty pages |
| `faculty/css/faculty.css` | shared faculty visual theme | faculty-specific cards, identity styling | page theme becomes inconsistent | faculty page classes | most faculty pages |
| `faculty/css/dashboard.css` | dashboard styling | dashboard card layout | dashboard degrades visually | dashboard markup | dashboard |
| `faculty/css/attendance.css` | attendance styling | class table and radio controls | attendance page degrades | attendance markup | attendance |
| `faculty/css/marks.css` | marks entry styling | large editable marks table UI | marks page becomes difficult to use | marks markup | marks |
| `faculty/css/students.css` | student lookup styling | student table, risk modal, alert modal | students page degrades | student lookup markup | students |
| `faculty/css/notifications.css` | inbox/send notice styling | notification tabs/cards/forms | notifications page degrades | notification markup | notifications |

## `FrontEnd/hod/`

### HOD components

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `hod/components/header.html` | HOD top bar fragment | reusable shell | header disappears | CSS classes | `hod/js/main.js` |
| `hod/components/sidebar.html` | HOD nav fragment | HOD page navigation | navigation disappears | route URLs, CSS | `hod/js/main.js` |

### HOD HTML pages

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `hod/html/dashboard.html` | HOD home page | HOD welcome card and profile summary | landing page disappears | `hod/js/dashboard.js` | HOD |
| `hod/html/profile.html` | HOD profile edit page | allows profile load/update | profile screen disappears | `hod/js/hod_profile.js` | HOD |
| `hod/html/students.html` | student analytics page | single student lookup + batch analytics + alerts | student analytics UI disappears | `hod/js/students.js`, Chart.js | HOD |
| `hod/html/faculty.html` | faculty lookup page | faculty search and targeted notification modal | faculty oversight UI disappears | `hod/js/faculty.js` | HOD |
| `hod/html/timetable.html` | timetable upload page | class/faculty timetable upload interface | timetable admin UI disappears | `hod/js/timetable.js` | HOD |
| `hod/html/notifications.html` | HOD notification page | send notices and view inbox | HOD notification UI disappears | `hod/js/notifications.js` | HOD |
| `hod/html/fees.html` | placeholder HOD fees page | static/partial page with referenced missing JS | very little runtime impact now | CSS and possibly missing script | likely incomplete |

### HOD JavaScript

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `hod/js/main.js` | shared HOD shell logic | loads components, rewrites API base, logout | HOD shell breaks | DOM, components | all HOD pages |
| `hod/js/dashboard.js` | HOD dashboard loader | fetches own profile and fills home page | dashboard stays empty | `/hod/profile` | `dashboard.html` |
| `hod/js/hod_profile.js` | HOD profile load/update logic | edits HOD profile through API | profile page breaks | `/hod/profile` | `profile.html` |
| `hod/js/students.js` | HOD student lookup/analytics logic | student detail lookup, analytics charts, alert sending | major HOD functionality breaks | `/hod/student/*`, `/hod/students-analytics`, `/hod/alerts/send` | `students.html` |
| `hod/js/faculty.js` | HOD faculty search/list/alert logic | lookup faculty list/details and send faculty notices | faculty management page breaks | `/hod/faculty`, `/hod/view/faculty/*`, `/hod/notifications` | `faculty.html` |
| `hod/js/timetable.js` | timetable upload logic | sends timetable image uploads for class or faculty | timetable page breaks | `/hod/timetable/upload` | `timetable.html` |
| `hod/js/notifications.js` | HOD send/inbox notification logic | sends role-targeted notices and renders inbox | notifications page breaks | `/hod/notifications` | `notifications.html` |

### HOD CSS

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `hod/css/components.css` | shared HOD shell styling | common layout | shell degrades | components markup | all HOD pages |
| `hod/css/hod.css` | HOD visual theme | HOD-specific cards/forms styling | theme degrades | HOD page classes | most HOD pages |
| `hod/css/dashboard.css` | dashboard styling | home page card layout | dashboard degrades | dashboard markup | dashboard |
| `hod/css/students.css` | student analytics styling | lookup/result tables/charts | students page degrades | students markup | students |
| `hod/css/faculty.css` | faculty lookup styling | faculty table and cards | faculty page degrades | faculty markup | faculty |
| `hod/css/notifications.css` | notification page styling | tabs/cards/forms | notification page degrades | notification markup | notifications |
| `hod/css/fees.css` | HOD fees page styling | styles incomplete page | mostly cosmetic loss | fees markup | fees |

## `FrontEnd/student/`

### Student components

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `student/components/header.html` | student top bar fragment | reusable student shell | header disappears | CSS classes | `student/js/main.js` |
| `student/components/sidebar.html` | student nav fragment | student module navigation | navigation disappears | page URLs, logout handler, CSS | `student/js/main.js` |

### Student HTML pages

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `student/html/dashboard.html` | student home page | dashboard stats, AI alert, timetable | landing page disappears | `student/js/dashboard.js` | student |
| `student/html/profile.html` | student profile page | personal/academic/contact details | profile screen disappears | `student/js/profile.js` | student |
| `student/html/academic.html` | marks/results page | internal/external marks and GPA with PDF export | academic view disappears | `student/js/academic.js`, jsPDF libs | student |
| `student/html/attendance.html` | attendance page | monthly register and semester summary | attendance screen disappears | `student/js/attendance.js` | student |
| `student/html/fees.html` | fees page | fee structure, transactions, payment submit, receipt print | fees screen disappears | `student/js/fees.js`, jsPDF | student |
| `student/html/hostel.html` | hostel page | hostel allocation view | hostel page disappears | `student/js/hostel.js` | student |
| `student/html/library.html` | library page | library issued books view | library page disappears | `student/js/library.js` | student |
| `student/html/notifications.html` | notifications page | combined notifications + alerts inbox | notification screen disappears | `student/js/notifications.js` | student |

### Student JavaScript

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `student/js/main.js` | shared student shell logic | loads components, rewrites API base, nav highlighting, logout | student shell breaks | DOM, components | all student pages |
| `student/js/dashboard.js` | dashboard loader | fetches dashboard aggregate and timetable | home page stays blank | `/student/dashboard`, `/student/timetable` | `dashboard.html` |
| `student/js/profile.js` | profile loader | fetches profile + academics and fills fields | profile page breaks | `/student/profile`, `/student/my-academics` | `profile.html` |
| `student/js/academic.js` | academic records logic | switches between internal/external views and exports PDF | academic page breaks | marks APIs, jsPDF | `academic.html` |
| `student/js/attendance.js` | attendance analytics logic | monthly table transform + semester summary rendering | attendance page breaks | attendance/student APIs | `attendance.html` |
| `student/js/fees.js` | fee/payment workflow | structure/transactions render, student payment submit, receipt generation | fees page breaks | student payment APIs | `fees.html` |
| `student/js/hostel.js` | hostel allocation renderer | shows hostel allocation state | hostel page breaks | `/student/hostel` | `hostel.html` |
| `student/js/library.js` | library student view | fetches and filters issued books, updates counts | library page breaks | `/library/student/books` | `library.html` |
| `student/js/notifications.js` | notifications+alerts renderer | loads both system notifications and direct alerts | inbox page breaks | `/student/notifications`, `/student/alerts` | `notifications.html` |

### Student CSS

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `student/css/components.css` | shared student shell styling | sidebar/header/common layout | shell degrades | component markup | all student pages |
| `student/css/dashboard.css` | dashboard styling | dashboard card layouts and alert box visuals | dashboard degrades | dashboard markup | dashboard |
| `student/css/profile.css` | profile styling | profile cards/rows | profile readability drops | profile markup | profile |
| `student/css/academic.css` | academic table styling | marks and GPA UI | academic page degrades | academic markup | academic |
| `student/css/attendance.css` | attendance table styling | attendance matrix and summary cards | attendance page degrades | attendance markup | attendance |
| `student/css/fees.css` | fees styling | fee tables, modal, receipt-related visuals | fees page degrades | fees markup | fees |
| `student/css/hostel.css` | hostel styling | allocation card visuals | hostel page degrades | hostel markup | hostel |
| `student/css/library.css` | library styling | stats cards and issue table visuals | library page degrades | library markup | library |
| `student/css/notifications.css` | notifications styling | cards/tabs/badges | notifications page degrades | notifications markup | notifications |

## `Academic_Early_Warning_System/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `backend/inference.py` | older standalone inference script | preserves prototype ML inference logic used during development | deployed app still works; research traceability declines | joblib, shap, pandas | ML experimentation |
| `data/original/student_records.csv` | raw dataset | source data for training notebook | retraining and audit trail weaken | none | notebook |
| `data/processed/train_normalized.csv` | processed training split | supports reproducible ML experiments | training reproducibility drops | notebook pipeline | notebook |
| `data/processed/test_normalized.csv` | processed test split | supports reproducible evaluation | evaluation reproducibility drops | notebook pipeline | notebook |
| `notebooks/Academic_Early_Warning_System.ipynb` | main training notebook | feature engineering, XGBoost training, artifact export | training workflow knowledge is lost | pandas/sklearn/xgboost/shap | model development |

## `uploads/`

| File | What it is | Why needed | If removed | Depends on | Used by |
|---|---|---|---|---|---|
| `uploads/timetables/students/CSM_1_2_A.png` | sample class timetable image | proves student timetable upload/output path | only that timetable disappears | timetable upload | student timetable view |
| `uploads/timetables/faculty/ramu@vvit.net.png` | sample faculty timetable image | proves faculty timetable upload/output path | only that timetable disappears | timetable upload | faculty timetable view |

---

## Level 3: Code-Level Analysis

This section goes deeper into the important runtime files.

For static HTML/CSS/component files, the file inventory above already explains:

- what they are
- why they exist
- what breaks if removed
- what they depend on
- what depends on them

The deepest logic sits in:

- backend entry/config/auth/db files
- routers
- services
- models
- frontend JavaScript files

## Backend Core Deep Walkthrough

### `Backend/app/main.py`

Purpose:

- creates the FastAPI app instance
- mounts static uploaded files
- configures CORS
- includes all routers

Imports:

- all router modules
- `FastAPI`
- `CORSMiddleware`
- `StaticFiles`
- `os`

Line-by-line behavior:

1. imports router objects from each domain module
2. creates `app = FastAPI(title="ERP Student Management System")`
3. computes `BASE_DIR` from current file path
4. mounts `/uploads` to `../uploads`
5. adds CORS middleware
6. includes all routers one by one

Why each variable exists:

- `app`: the ASGI application object uvicorn serves
- `BASE_DIR`: resolves the uploads path relative to the file location instead of relying on current working directory

Important design effect:

- timetable image metadata stores relative paths like `uploads/timetables/...`
- the mounted static directory makes those files web-accessible

Dependencies:

- depends on every router module
- depends on filesystem uploads folder

Dependents:

- uvicorn command in Dockerfile
- local `uvicorn app.main:app`

Code review note:

- CORS currently allows `*`, which is permissive and not ideal for production

### `Backend/app/core/config.py`

Purpose:

- centralizes configuration loading from environment variables

Variables:

- `JWT_SECRET`: signing key for JWT
- `JWT_ALGORITHM`: hardcoded as `HS256`
- `JWT_EXPIRE_MINUTES`: token TTL
- `DATABASE_URL`: SQLAlchemy connection string
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SENDER_EMAIL`: mail settings
- `PASSWORD_RESET_BASE_URL`: reset page URL included in email

Why this file matters:

- without it, the backend would hardcode runtime secrets in many different files

Code review notes:

- there is a default JWT secret in code; production should not rely on defaults
- root `.env.example` uses `SECRET_KEY`, while runtime code expects `JWT_SECRET`; that is a configuration mismatch

### `Backend/app/core/database.py`

Purpose:

- initializes SQLAlchemy engine and session factory

Objects:

- `engine`: connection engine created from `DATABASE_URL`
- `SessionLocal`: sessionmaker for per-request DB sessions
- `Base`: declarative base for models
- `get_db()`: generator dependency that yields a DB session and closes it

Connection flow:

- models inherit from `Base`
- routers/services receive `db: Session = Depends(get_db)`

If removed:

- all ORM models and DB sessions fail

### `Backend/app/core/security.py`

Purpose:

- password hashing and JWT creation

Objects:

- `pwd_context`: Passlib context configured with `argon2`
- `hash_password(password)`
- `verify_password(password, hashed)`
- `create_jwt(email, role)`

Why `argon2`:

- stronger password hashing than simple hashing or plain text

JWT payload structure:

- `sub`: user email
- `role`: user role
- `exp`: expiry timestamp

Code review note:

- file contains a commented-out old implementation using bcrypt; that is legacy noise and should be cleaned

### `Backend/app/core/dependencies.py`

Purpose:

- extracts and validates bearer tokens from incoming requests

Key objects:

- `security = HTTPBearer()`
- `get_current_user(credentials=Depends(security))`

Logic:

1. FastAPI parses `Authorization: Bearer ...`
2. token is extracted from `credentials.credentials`
3. token is decoded with secret and algorithm
4. payload is returned directly

Returned payload shape:

- at least `sub` and `role`

Code review notes:

- imports and `security` declaration are duplicated inside the file
- exception handling mixes `jwt.ExpiredSignatureError` and `jwt.InvalidTokenError`; with `python-jose`, dedicated exception handling should be cleaned up for correctness/readability

## Backend Model Deep Walkthrough

### Identity and profile models

#### `models/user.py`

Class: `User`

Columns:

- `id`: primary key
- `email`: unique login identifier
- `password`: hashed password
- `role`: enum `STUDENT | FACULTY | HOD | ADMIN`
- `personal_email`: fallback email for password recovery
- `reset_token`: password reset token
- `reset_token_expiry`: expiry timestamp
- `is_active`: soft active flag

Why it exists:

- separates authentication identity from role-specific profile data

#### `models/student.py`

Class: `Student`

Columns:

- identity: `id`, `user_email`, `personal_email`, `roll_no`
- personal: `first_name`, `last_name`, `gender`, `blood_group`, `date_of_birth`
- contact: `mobile_no`, `parent_mobile_no`, `address`, `parentname`
- residential/academic identity: `residence_type`, `branch`, `section`, `batch`, `course`, `quota`, `admission_date`

Why this duplication exists:

- some academic identity fields appear both in `students` and `academics`
- `students` behaves like the relatively stable student master profile
- `academics` behaves like semester/year-specific academic state

#### `models/faculty.py`

Class: `Faculty`

Stores:

- faculty identity by `user_email`
- personal and contact data
- academic assignment fields: `subject_code`, `subject_name`, `branch`

#### `models/hod.py`

Class: `HODProfile`

Stores:

- HOD identity and profile data
- assigned `branch`

#### `models/admin.py`

Class: `AdminProfile`

Stores:

- admin `email`
- `name`
- `mobile_no`
- `designation`

### Academic models

#### `models/academic.py`

Class: `Academic`

Columns:

- `academic_id`: PK
- link fields: `sid`, `user_email`, `srno`
- academic descriptors: `branch`, `batch`, `course`, `year`, `semester`, `section`, `type`, `quota`
- lifecycle: `admission_date`, `status`

Why this table exists:

- stores the student’s academic state separate from personal profile
- used heavily for joins and context resolution

#### `models/internal_marks.py`

Class: `InternalMarks`

Stores:

- student+subject+semester identity
- raw Mid 1 components
- raw Mid 2 components
- computed `mid1`
- computed `mid2`
- computed `final_internal_marks`
- `entered_by`

Why both raw and derived values are stored:

- raw components are needed for editable UI and auditability
- derived fields avoid recalculating everything every time

#### `models/external_marks.py`

Class: `ExternalMarks`

Stores:

- student+subject+semester external exam marks
- credits
- batch/branch/section context
- computed grade
- `entered_by`

#### `models/course_grade.py`

Class: `CourseGrade`

Stores fully derived per-subject semester result:

- internal marks
- external marks
- total semester marks
- grade letter
- grade points

Class: `SemesterGrade`

Stores per-semester aggregate result:

- `sgpa`
- `cgpa`
- `cgpa_percentage`
- `total_credits`
- `result_status`

#### `models/semester_result.py`

Legacy result table.

Current code mainly uses `SemesterGrade`, not this model.

This means:

- it exists for compatibility or older design
- it is not the main table for current transcript/result APIs

### Attendance models

#### `models/attendance_session.py`

Represents one attendance event:

- subject
- year
- semester
- date
- period
- faculty email

#### `models/attendance_record.py`

Represents one student’s status inside one session:

- `session_id`
- `sid`
- `srno`
- `status`

Together these two tables implement a header-detail attendance design.

### Fee/hostel/library/timetable/message models

#### `models/fee_structure.py`

Stores fee master amounts by:

- `quota`
- `residence_type`
- `year`

and fee components:

- tuition
- bus
- hostel

#### `models/payment.py`

Stores each payment transaction independently:

- `receipt_id`
- `srno`
- `student_email`
- `fee_type`
- `amount_paid`
- `payment_mode`
- `status`
- `description` for serialized payment metadata
- year/semester/date/updater

Important design choice:

- each payment submission creates a new row, not an in-place update

#### `models/hostel_room.py`

Stores:

- unique room number
- sharing
- room type
- capacity
- occupied count
- active flag

#### `models/hostel_allocation.py`

Stores:

- `student_id`
- `room_id`
- allocation and vacation dates
- lifecycle `status`
- `allocated_by`

#### `models/library_books.py`

Stores book catalog:

- `code`
- `title`
- `author`
- `available_copies`

#### `models/library_issue.py`

Stores library transactions:

- student roll number
- borrowed book code
- semester/year context
- issued date
- expected return date
- actual return date
- status
- updater

#### `models/timetable.py`

Stores uploaded timetable metadata:

- class/faculty context
- image path
- uploader

#### `models/notification.py`

Stores broad inbox notifications with targeting fields:

- role
- batch
- branch
- section
- target_email
- category
- priority
- sender_role
- created_by
- created_at

#### `models/alert.py`

Stores direct alert messages tied to:

- `student_roll`
- sender identity
- message metadata
- severity
- read state

## Backend Router and Service Deep Walkthrough

### `routers/auth.py` + `services/auth_service.py`

Endpoints:

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/change-password`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`

#### `signup(...)`

What it does:

1. validates that email ends with `@vvit.net`
2. requires `personal_email`
3. normalizes email and role
4. rejects invalid roles
5. checks if user already exists
6. hashes password
7. inserts `User`
8. auto-creates empty HOD or Admin profile when role is HOD/ADMIN

Why:

- keeps auth identity creation and role-specific bootstrap together

#### `login(...)`

What it does:

1. validates email format/domain
2. fetches active user
3. verifies password hash
4. optionally verifies selected role matches stored role
5. returns JWT token

Returned response shape:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

#### `change_password(...)`

What it does:

1. fetches active user by email from token payload
2. verifies old password
3. hashes and saves new password

#### `request_password_reset(...)`

What it does:

1. validates institutional email
2. loads active user
3. ensures personal email exists
4. generates secure token
5. stores token and expiry in DB
6. creates reset link using `PASSWORD_RESET_BASE_URL`
7. sends email via SMTP

#### `verify_reset_token_and_update_password(...)`

What it does:

1. loads user
2. checks token equality
3. checks expiry
4. updates password
5. clears token fields

Code review notes:

- signup email validation is domain-restricted; this matches campus requirement but reduces portability
- password reset depends completely on SMTP configuration being correct

### `routers/student.py`

This is the largest student-facing router.

Important note:

- the file contains duplicate imports and two `router = APIRouter(...)` definitions caused by legacy merge/duplication
- runtime still works because the later router object is the effective one used by the decorators below it

Major endpoints:

- `GET /student/dashboard`
- `GET /student/profile`
- `PUT /student/profile`
- `GET /student/my-academics`
- `GET /student/payments`
- `POST /student/payments/submit`
- `GET /student/internal-marks/{year}/{semester}`
- `GET /student/external-marks/{year}/{semester}`
- `GET /student/attendance/monthly`
- `GET /student/attendance/summary`
- `GET /student/attendance/subject-wise`
- `GET /student/hostel`
- `GET /student/timetable`
- `GET /student/notifications`
- `GET /student/alerts`

#### `GET /student/dashboard`

Logic:

1. checks role is `STUDENT`
2. loads `Student` by token email
3. loads latest `Academic` row to infer current semester
4. computes attendance percentage from `attendance_service`
5. loads `SemesterGrade` rows to compute `cgpa` / previous `sgpa`
6. counts backlogs from `ExternalMarks` grade `F`
7. loads `InternalMarks` for current semester and averages `mid1`/`mid2`
8. builds feature vector:
   - `mid1_exam_30`
   - `mid2_exam_30`
   - `attendance_pct_100`
   - `prev_year_sgpa_10`
   - `backlogs`
9. calls local ML inference
10. loads payment summary
11. loads library book count
12. returns profile block + stats block + AI insight string

Response shape:

```json
{
  "profile": {
    "name": "Student Name",
    "roll_no": "22BQ1A....",
    "branch": "CSE",
    "semester": 3
  },
  "stats": {
    "attendance": 82.5,
    "cgpa": 7.8,
    "fee_dues": 12000,
    "library_books": 2
  },
  "ai_insight": "Moderate Risk ..."
}
```

#### `PUT /student/profile`

Uses `student_service.upsert_student_profile`.

The service:

1. fetches student by email
2. creates one if missing
3. assigns all request fields to DB columns
4. saves and refreshes

#### `GET /student/payments`

Input:

- query `semester`

Output:

- fee structure summary
- transaction list

Uses `payment_service.get_student_payment_details`.

#### `POST /student/payments/submit`

Converts student payment form into `PaymentUpdateRequest` shape and reuses admin payment service logic.

That means:

- admin and student payment submissions share one transaction creation implementation

#### Attendance endpoints

They delegate to `attendance_service` functions:

- monthly detailed register
- semester summary
- subject-wise summary

#### `GET /student/timetable`

Logic:

1. load current academic context
2. query timetable by `year + semester + section + branch`
3. if found, build absolute image URL from request base URL and stored `image_path`

#### `GET /student/notifications`

Logic:

1. enforce role `STUDENT`
2. load student academic context
3. fetch notifications matching role + batch + branch + section + target email

#### `GET /student/alerts`

Logic:

1. load student profile by email
2. find direct alerts by roll number
3. return newest first

### `routers/student_grades.py`

Purpose:

- gives more structured academic APIs than the legacy `/student/external-marks/{year}/{semester}` route

Endpoints:

- `GET /student/marks/internal/{semester}`
- `GET /student/marks/external/{semester}`
- `GET /student/transcript`
- `GET /student/semester-results/{semester}`

#### Internal marks endpoint

Returns per-subject internal component breakdown for either Mid 1 or Mid 2 using query `mid=1|2`.

#### External marks endpoint

Returns:

- subject list with internal/external/semester marks
- credits
- grade letter
- grade points
- semester `sgpa`
- overall `cgpa`
- `cgpa_percentage`
- `result_status`

#### Transcript endpoint

Returns all semester rows with:

- SGPA
- total credits
- status
- overall CGPA and equivalent percentage

### `routers/faculty.py`

Major endpoints:

- profile read/update
- student lookup by roll number
- internal marks upload/get/update
- attendance mark/view
- timetable view
- class student list
- notifications send/inbox
- comprehensive student list
- direct student alerts

#### `GET /faculty/class-students`

Inputs:

- `batch`
- optional `branch`
- optional `section`

Logic:

1. joins `Student` and `Academic`
2. filters by batch
3. optionally filters branch/section
4. returns distinct roll numbers and names

This endpoint is used by both:

- attendance page
- marks entry page

#### `POST /faculty/internal-marks/upload`

Inputs:

- `subject_code`
- `semester`
- uploaded Excel file
- optional batch/year/branch/section

Logic:

1. checks role
2. resolves year from batch/semester/year
3. delegates to `upload_internal_marks_excel`

#### `POST /faculty/internal-marks/get`

Uses `internal_marks_service.get_internal_marks`.

It fetches one student-subject record by roll number and subject key.

#### `PUT /faculty/internal-marks/update`

Uses `internal_marks_service.update_internal_marks`.

That service:

1. locates student-subject-semester row
2. creates row if missing
3. copies all raw components
4. recalculates `mid1` and `mid2`
5. commits

#### `POST /faculty/attendance/mark`

Uses `attendance_service.mark_attendance`.

That service:

1. checks if an attendance session already exists for same subject/date/period/semester
2. if yes, deletes old records and old session
3. creates a new session
4. iterates submitted attendance items
5. resolves each roll number to student
6. inserts one `AttendanceRecord` per student
7. commits

Important design effect:

- marking attendance again for the same period overrides old attendance instead of creating duplicates

#### `GET /faculty/student-list`

This returns a wide student dataset for faculty advisory use:

- identity
- mobile
- academic status
- residence
- quota
- payment records

It is consumed by the faculty student lookup page.

#### `POST /faculty/notifications`

Faculty can only send to students.

Validation steps:

- sender email must be valid
- target email, if given, must be valid
- target role must be `STUDENT`
- batch is mandatory
- `ALL` branch/section are normalized to `null`

#### `POST /faculty/alerts/send`

Creates direct `Alert` row tied to student roll number.

### `routers/hod.py`

Major capabilities:

- HOD profile
- notifications
- timetable upload
- department faculty list
- student analytics
- student lookup
- faculty detail view
- student alerts

#### `GET /hod/students-analytics`

This is the HOD analytics backbone.

Inputs:

- batch
- branch
- semester
- section

Logic:

1. normalizes filters
2. if semester is absent, derives latest semester per student using subquery
3. loads `Student + Academic`
4. loads one `InternalMarks` row to compute Mid1/Mid2
5. loads attendance summary
6. returns analytics rows with roll, name, m1, m2, attendance, parent phone, branch, section, semester

This output feeds both:

- analytics table
- Chart.js distributions

#### `POST /hod/timetable/upload`

Inputs:

- form data: year, semester, branch, and either section or faculty email
- file upload

Delegates to `timetable_service.upload_timetable_image`.

That service:

1. validates required context
2. chooses folder `uploads/timetables/students` or `uploads/timetables/faculty`
3. generates filename
4. writes file to disk
5. inserts `TimeTable` row

### `routers/admin.py`

This is the heaviest operational router.

Major endpoint groups:

- admin profile
- admissions upload
- fee structure create/bulk-create
- external marks upload
- hostel upload/CRUD/allocation/statistics
- student/faculty/HOD list retrieval
- dashboard stats/activity
- notifications

#### `POST /admin/upload-students`

Despite the endpoint name, it can upload:

- students
- faculty
- HOD

Inputs:

- Excel file
- query `role`
- query `semester`

Delegates to `excel_service.process_excel`.

#### `process_excel(...)`

Shared import pipeline:

1. loads workbook
2. chooses branch by role:
   - `_process_student_excel`
   - `_process_faculty_excel`
   - `_process_hod_excel`
3. commits

##### Student import path

For each row:

1. extracts columns
2. skips empty email
3. skips existing student email or duplicate roll
4. creates `Student`
5. flushes to get ID
6. creates `Academic`
7. creates initial `Payment` seed records if fee structure exists

##### Faculty/HOD import path

For each row:

1. extracts dynamic columns by header name
2. ensures login `User` exists via `_ensure_user`
3. upserts faculty or HOD profile data

#### `POST /admin/external-marks/upload/{batch}/{semester}`

Delegates to `excel_marks_service.upload_external_marks_excel`.

That function is one of the most important in the system.

Detailed logic:

1. open workbook
2. normalize headers if present
3. iterate rows as `(roll_no, subject_code, subject_name, credits, external_marks)`
4. find student
5. find matching academic row by batch and optional branch/section
6. load internal marks for same student/subject/semester
7. compute:
   - semester total = internal + external
   - grade letter
   - grade points
8. upsert `ExternalMarks`
9. upsert `CourseGrade`
10. accumulate total grade points and credits by student
11. after all rows, compute SGPA and CGPA per student
12. upsert `SemesterGrade`

This is the final result generation pipeline.

#### Hostel admin endpoints

These call `hostel_service` for:

- room upload
- allocate
- vacate
- stats
- room CRUD
- allocation list
- allocation status update

### `routers/library.py`

Endpoints:

- `GET /library/books`
- `POST /library/books/upload`
- `POST /library/issue`
- `POST /library/return`
- `GET /library/pending`
- `GET /library/student/books`

Key service logic:

- upload increases or inserts catalog copies
- issue decrements `available_copies`
- return increments `available_copies`
- student view joins issue rows to catalog rows

### `routers/payment.py` + `services/payment_service.py`

Important functions:

#### `get_payment_details_by_roll(db, roll_no)`

Logic:

1. load student by roll number
2. load one academic row
3. load fee structure by quota/residence/year
4. load payments for same student/year
5. build fee map:
   - tuition
   - bus
   - hostel
6. compute `paid` and `balance` per fee type

#### `update_student_payment(db, req, admin_email)`

Logic:

1. load latest academic record for student
2. load student
3. normalize fee type
4. generate unique `receipt_id`
5. create a brand new `Payment` row with `PENDING`
6. serialize `payment_details` into `description` if present
7. commit

Why this design:

- preserves a transaction log instead of overwriting existing payment row

#### `get_student_payment_details(db, student_email, semester)`

Logic:

1. load student
2. convert global semester number to year + odd/even semester
3. load corresponding academic row
4. load fee structure
5. load payment rows for that year
6. aggregate paid amount by fee type
7. build:
   - `structure`: total, paid, balance, status
   - `transactions`: dated transaction history with remaining balance after each payment

Code review notes:

- `payments/my` route uses `user["sub"]` as roll number but JWT stores email; that path appears inconsistent and likely unused compared with the student-specific `/student/payments`
- `Payment.status` is set to `PENDING` even when payment is recorded, so fee-status semantics across UI are slightly confusing

### `services/notification_service.py`

This file encodes notification targeting rules.

#### `create_notification(...)`

Creates notification row with sender metadata and targeting fields.

#### `get_student_notifications(...)`

Filters by:

- target role `ALL` or `STUDENT`
- matching batch or `NULL`
- matching branch or `NULL`
- matching section or `NULL`
- matching target_email or `NULL`

This is the inbox delivery rule engine for students.

#### `get_faculty_notifications(...)`

Allows:

- broad notifications targeted to faculty/all with branch and optional target email
- plus notifications faculty themselves created

#### `get_hod_notifications(...)`

Allows:

- broad notifications for all/HOD
- optional direct email targeting

### `services/attendance_service.py`

Important functions:

- `mark_attendance`
- `get_student_attendance`
- `get_student_monthly_attendance`
- `get_semester_attendance_summary`
- `get_subject_wise_attendance`
- `get_low_subjects`

`get_student_monthly_attendance` returns:

- per-date grouped class records
- per-subject totals
- overall monthly totals

`get_semester_attendance_summary` returns:

- total classes
- attended classes
- absent classes
- percentage
- exam eligibility using threshold `>= 75`

`get_low_subjects`:

- reuses subject-wise attendance
- filters those below threshold
- calculates shortfall amount

### `services/inference.py`

Purpose:

- runtime ML inference for academic risk

Startup behavior:

1. loads model, scaler, and feature-order artifacts
2. creates a minimal SHAP explainer background array
3. gracefully falls back to unavailable model message if load fails

#### `predict_student_risk(student_dict)`

Input:

- dictionary keyed by model feature names

Logic:

1. fills missing features with zero
2. creates pandas DataFrame in exact feature order
3. scales input
4. gets positive-class probability
5. runs SHAP explanation
6. collects features with positive SHAP contribution
7. maps probability to:
   - low
   - moderate
   - high
8. returns readable multi-line string

#### `predict_student_risk_structured(student_dict)`

Same logic but returns JSON-friendly dict:

```json
{
  "risk_level": "LOW|MEDIUM|HIGH",
  "risk_probability": 42.3,
  "explanation": "Main risk factors: ..."
}
```

Code review note:

- SHAP explanation is wrapped in try/except, which is good because SHAP failures should not block the entire dashboard

### `services/ai_service.py`

Purpose:

- sends low-attendance data to Gemini `generateContent`

Prompt content enforces:

- short output
- max four bullet points
- attendance threshold context

Code review notes:

- this is a live external network call and needs network access and valid API key
- no retry/backoff logic exists
- if the service returns an error JSON, user receives error text directly

## Frontend JavaScript Deep Walkthrough

### `FrontEnd/script.js`

Purpose:

- login-page logic

Global variables:

- `API_BASE`: runtime host + port 8000
- `LOCAL_API_ORIGIN`: hardcoded local origin
- `_origFetch`: preserved browser fetch

Why the fetch wrapper exists:

- all page scripts hardcode `http://127.0.0.1:8000`
- when deployed, this wrapper rewrites those calls to current host on port 8000

Main functions:

- `showForm(formName)`: toggles among login/change-password/forgot/reset forms
- `toggleForms()`: older compatibility helper

Event handlers:

- login form submit:
  1. validate fields
  2. call `POST /auth/login`
  3. decode JWT payload
  4. store token in `localStorage`
  5. redirect based on role
- change password:
  1. first login with old password to obtain temporary token
  2. call `POST /auth/change-password`
- forgot password:
  1. validates `@vvit.net`
  2. calls `POST /auth/forgot-password`
- reset password:
  1. validates matching passwords
  2. calls `POST /auth/reset-password`
- page load:
  1. reads `token` and `email` from query string
  2. auto-opens reset form if present

Security note:

- JWT is stored in `localStorage`, which is easy for static apps but weaker than `httpOnly` cookies

### `student/js/main.js`, `faculty/js/main.js`, `hod/js/main.js`, `admin/js/main.js`

Shared pattern:

1. redirect to login if token is missing
2. rewrite hardcoded local API URL to deployment host
3. load sidebar and header HTML fragments using `fetch`
4. highlight current page link
5. define logout behavior

Why this exists:

- avoids duplicating common shell markup across every page

### `student/js/dashboard.js`

Functions:

- `initDashboard()`
- `updateStat(id, value)`
- `loadTimetable()`

Dashboard flow:

1. render current date
2. verify token exists
3. fetch `/student/dashboard`
4. fill:
   - welcome name
   - profile name
   - semester
   - branch
   - attendance gauge
   - CGPA
   - fee due text
   - library count
5. parse `ai_insight` text to choose alert-box color and label
6. fetch `/student/timetable` and render image if available

Interesting dependency:

- risk level styling is inferred from the returned AI text string rather than a structured risk field

### `student/js/academic.js`

Functions:

- `getAuthHeaders`
- `mid1Total`
- `mid2Total`
- `updateTable`
- `loadInternalMarks`
- `loadSemesterMarks`
- `downloadPdf`

Flow:

1. user selects semester and exam type
2. if `mid1` or `mid2`, frontend calls legacy route `/student/internal-marks/{year}/{semester}`
3. if `semester`, frontend calls legacy route `/student/external-marks/{year}/{semester}`
4. renders table and SGPA/CGPA/status
5. export uses jsPDF and autoTable

Code review note:

- this page consumes the legacy routes from `student.py`, not the richer newer routes from `student_grades.py`

### `student/js/attendance.js`

Functions:

- `preloadAcademicInfo`
- `loadAttendance`
- `transformData`
- `renderTable`
- `loadSemesterOverview`
- `clearSemesterOverview`

Flow:

1. preload latest batch/semester from `/student/my-academics`
2. call `/student/attendance/monthly`
3. convert date-grouped API payload into day-column matrix
4. render per-subject `P/A/L/-`
5. compute monthly totals on client
6. separately call summary and subject-wise endpoints

### `student/js/fees.js`

Functions:

- `updateFeeView`
- `downloadReceipt`
- modal open/close helpers
- `updatePaymentModeFields`
- `submitStudentPayment`
- `displayPaymentReceipt`

Flow:

1. fetch `/student/payments?semester=...`
2. render fee structure totals and transaction table
3. allow student to submit payment details
4. send `POST /student/payments/submit`
5. open printable receipt window
6. refresh fee view

Important data design:

- UPI and DD extra details are collected and sent as nested `payment_details`

### `faculty/js/marks.js`

Main functions:

- `fetchStudentListForMarks`
- `fetchStudentMarks`
- `calcTotals`
- `toggleABMarks`
- `submitMarks`
- `downloadMarksExcelTemplate`
- `uploadMarksExcel`

Flow:

1. fetch students for a class from `/faculty/class-students`
2. for each student, fetch existing internal marks from `/faculty/internal-marks/get`
3. allow inline editing of raw components
4. calculate Mid1/Mid2 totals on client instantly
5. submit row-by-row to `/faculty/internal-marks/update`
6. alternatively upload Excel to `/faculty/internal-marks/upload`

### `faculty/js/attendance.js`

Main functions:

- `fetchStudentListForAttendance`
- `calculateSummary`
- `updateSummary`
- `submitAttendance`

Flow:

1. fetch class list using batch/branch/section
2. render one row per student with present/absent radio buttons
3. compute live summary counts
4. build attendance payload:

```json
{
  "subject_code": "...",
  "subject_name": "...",
  "batch": "2022-26",
  "semester": 3,
  "date": "2026-04-09",
  "period": 2,
  "attendance": [
    {"roll_no": "...", "status": "PRESENT"}
  ]
}
```

5. send to `/faculty/attendance/mark`

### `faculty/js/students.js`

This is one of the richest frontend files.

Responsibilities:

- load wide student list
- filter by search/fee/residence/branch/section
- compute fee status badge client-side
- open modal to send alerts
- call AI risk endpoint
- show risk modal
- convert risk modal into prefilled alert form

Key API calls:

- `GET /faculty/student-list`
- `GET /ai/aews/student-risk/{roll_no}`
- `POST /faculty/notifications`
- `POST /faculty/alerts/send`

Why it matters:

- this is where ERP data and AI advisory features meet for faculty intervention workflows

### `hod/js/students.js`

Responsibilities:

- single student lookup
- batch analytics fetch
- Chart.js rendering
- direct student alert modal

Key APIs:

- `GET /hod/student/{roll_no}`
- `GET /hod/students-analytics`
- `POST /hod/alerts/send`

### `admin/js/fees.js`

Responsibilities:

- create fee structure
- search student payment history
- render all-semester dues
- record new payment
- print receipt

Key APIs:

- `POST /admin/fee-structure`
- `GET /payments/payment/{roll_no}`
- `POST /payments/payment/update`

### `admin/js/hostel-new.js`

Responsibilities:

- fetch hostel statistics
- upload room sheet
- list rooms
- create/edit/delete room
- fetch hostel students
- allocate room
- view all allocations
- change allocation status

This file uses an `apiRequest` helper so all hostel API calls pass through a single auth-aware wrapper.

### Remaining frontend files that still matter

Even where a page script is not as logic-heavy as the ones above, it still has a role:

- `student/js/profile.js`: fetches `/student/profile`, hydrates profile form, submits profile update payload, keeps personal details editable without touching admin-imported master data manually in SQL.
- `student/js/hostel.js`: renders hostel allocation details and fee status returned by `/student/hostel`.
- `student/js/library.js`: displays books currently issued to the logged-in student from `/library/student-books`.
- `student/js/notifications.js`: lists role-targeted notifications and direct alerts, usually by calling `/student/notifications` and `/student/alerts`.
- `faculty/js/profile.js`: faculty-side equivalent of student profile editing.
- `faculty/js/faculty.js`: dashboard/profile helper file for faculty-specific widgets depending on page.
- `faculty/js/dashboard.js`: lighter wrapper that loads summary data and links faculty workflow cards.
- `faculty/js/notifications.js`: notification viewing and creation UI for faculty notices.
- `hod/js/hod_profile.js`: HOD profile management.
- `hod/js/faculty.js`: shows department faculty list from `/hod/faculty`.
- `hod/js/notifications.js`: HOD notice management.
- `hod/js/timetable.js`: image upload flow for timetable posting.
- `admin/js/dashboard.js`: admin statistics cards and recent activity.
- `admin/js/admissions.js`: bulk Excel upload entry point for student/faculty/HOD onboarding.
- `admin/js/library.js`: admin library catalog, issue, return, and pending-book screens.
- `admin/js/users.js`: admin-facing user/account listing workflows.
- `admin/js/results.js`: marks upload and result-processing views.
- `admin/js/students.js`: broad administrative student list and profile visibility page.
- every `components/header.html` and `components/sidebar.html`: repeated shell UI, role-specific navigation, logout buttons, and page layout anchoring.
- every CSS file under role folders: visual separation of concerns. Removing them usually does not break data flow, but it destroys usability and page structure.

## Remaining Backend Support Modules

### `routers/ai_route.py`

This router exposes the AI-specific APIs that do not fit neatly into pure ERP CRUD.

`_clamp_mid_component(value)`:

- converts malformed or missing exam values into safe float numbers
- enforces the invariant that a mid component cannot exceed 30
- exists because spreadsheets and manually updated records can contain dirty values

`_internal_mark_features(internals)`:

- iterates through `InternalMarks` rows
- extracts `mid1`, `mid2`, and `final_internal_marks`
- computes averaged features expected by the ML model
- returns three values:
  - `avg_mid1`
  - `avg_mid2`
  - `mid_avg` for UI explanation

`GET /ai/student/attendance/ai-advice`:

- input: `semester` query param
- auth: logged-in student
- logic:
  1. fetch student by JWT email
  2. call `get_low_subjects(...)`
  3. if no low-attendance subjects, return eligible response
  4. otherwise pass the low-attendance list to `get_attendance_advice(...)`
  5. return structured result with `eligible_for_exam`, `low_attendance`, and `ai_message`
- output format: JSON

`GET /ai/aews/student-risk/{roll_no}`:

- input:
  - path param `roll_no`
  - optional query param `semester`
- auth: faculty only
- logic:
  1. validate user role
  2. fetch student by roll number
  3. compute attendance summary using `attendance_service`
  4. get prior SGPA from `SemesterGrade`
  5. count current backlog/fail subjects from `ExternalMarks`
  6. gather internals from `InternalMarks`
  7. build model feature vector
  8. call `predict_student_risk_structured(...)`
  9. enrich response with academic metadata like branch, batch, section
- output:
  - `risk_level`
  - `risk_probability`
  - explanation text
  - visible factor breakdown

Why this file exists:

- it keeps AI orchestration separate from normal ERP CRUD routers

What breaks if removed:

- student AI attendance advice and faculty academic-risk prediction disappear

### `routers/academic.py`

This is a minimal router that exposes the student's academic records.

`GET /academic/my`:

- auth: student only
- fetches `Academic` rows by `user_email`
- returns `AcademicResponse` list

Why it exists despite overlap with `/student/academics`:

- likely historical separation where academic records were isolated as their own domain
- this indicates some route duplication in the project evolution

### `routers/admin_accounts.py`

Purpose:

- bulk-create login accounts from Excel without fully importing academic profile data

`upload_users(...)`:

- input:
  - query param `role`
  - uploaded Excel file
- logic:
  1. admin role check
  2. `extract_emails(file.file)` parses upload
  3. duplicate email detection
  4. `create_users_from_excel(...)` writes `User` rows
  5. returns counts of created, skipped, and errored users

This router depends on:

- `utils/excel_reader.py`
- `services/bulk_user_service.py`
- `core/dependencies.py`

### `services/excel_service.py`

This is the main bulk-ingestion engine for admin onboarding.

`_ensure_user(db, email, role, personal_email=None)`:

- upserts the base `User` authentication record
- generates random password using `bulk_user_service.generate_password()`
- hashes password using `security.hash_password()`
- ensures profile imports and login accounts stay synchronized

`_apply_if_value(model, attr, value)`:

- helper to avoid overwriting existing fields with blank values

`process_excel(file, db, admin_email, role="STUDENT", selected_semester=1)`:

- top-level Excel dispatcher
- loads workbook with `openpyxl`
- routes sheet processing to:
  - `_process_student_excel`
  - `_process_faculty_excel`
  - `_process_hod_excel`
- commits on success, rolls back on failure

`_process_student_excel(sheet, db, admin_email, selected_semester)`:

- expects a fixed column order
- for each row:
  1. skip blank email rows
  2. normalize email
  3. reject duplicates by email or roll number
  4. create `Student`
  5. flush to get `student.id`
  6. create initial `Academic` row
  7. create seed `Payment` rows using `_create_payment_records`

`_process_faculty_excel(sheet, db)`:

- reads header row and maps column indices by name
- deduplicates by email inside the upload
- creates or updates `Faculty`
- ensures corresponding `User` row exists

`_process_hod_excel(sheet, db)`:

- same pattern as faculty import, but writes `HODProfile`

`_calculate_year_from_batch(batch)`:

- infers current academic year from batch start year and current calendar year

`_create_payment_records(...)`:

- seeds `Payment` rows for fee categories based on fee structure and residence type
- creates pending tuition/bus/hostel payment rows

Why this file exists:

- admin onboarding by Excel is a core ERP workflow in real colleges

What happens if removed:

- admissions/import workflows break, and the system becomes manual-entry only

### `services/excel_marks_service.py`

This file is central to exam-result processing.

Low-level helpers:

- `_norm_header_cell(cell)`: standardizes Excel header text
- `_canonical_excel_col(norm)`: maps varying real-world sheet headers into canonical internal names
- `iter_external_marks_sheet_rows(sheet)`: iterates normalized external marks rows
- `convert_mark_value(value)`: safely converts marks, handling blanks and string noise

`upload_internal_marks_excel(...)`:

- reads faculty-uploaded internal marks workbook
- validates faculty identity and assigned subject
- parses row values like objective, descriptive, openbook, seminar for mid1 and mid2
- computes:
  - `mid1`
  - `mid2`
  - `final_internal_marks`
- writes/updates `InternalMarks`

`upload_external_marks_excel(...)`:

- reads admin-uploaded external marks workbook
- inserts/updates `ExternalMarks`
- joins with corresponding `InternalMarks`
- computes total semester score
- derives grade and grade points
- populates `CourseGrade`
- aggregates per-semester credits and points
- writes/updates `SemesterGrade`

This file is one of the most important in the whole repository because it turns raw assessment data into final academic outputs used by dashboards, transcripts, risk scoring, and interviews.

### `services/internal_marks_service.py`

`get_internal_marks(db, req)`:

- used by faculty to fetch class/subject/semester internal rows
- joins student metadata and mark records

`update_internal_marks(db, req)`:

- updates an individual student's internal record
- recalculates dependent values after edit

`get_internal_marks_by_student(db, student_roll_no, semester)`:

- student-facing read API for semester internal marks

### `services/external_marks_service.py`

`_serialize_external_row(em)`:

- turns ORM row into frontend-friendly dict

`get_semester_result(year, semester, db, user_email)`:

- student-side semester result fetcher
- finds student and academic context
- loads `ExternalMarks` and computed grade data
- returns results in a format usable by transcript and academic pages

### `services/student_service.py`

`get_student_by_email(db, email)`:

- simplest identity lookup helper

`upsert_student_profile(db, email, data)`:

- creates or updates student editable profile fields
- separates profile-management logic from router layer

### `services/faculty_service.py`

`get_faculty_by_email(db, email)`:

- profile lookup helper

`upsert_faculty_profile(db, email, data)`:

- updates faculty profile

`get_student_info_by_rollno(db, roll_no)`:

- assembles student profile + academic + fee data
- includes a fragile point: some code paths attempt `getattr(p, "amount", None)` even though the `Payment` model stores `amount_paid` and fee totals are usually derived from `FeeStructure`

### `services/admin_service.py`

Purpose:

- simple service wrapper for admin profile retrieval and update
- also contains `view_hod_profile(...)`, which suggests some service-boundary mixing

### `services/hod_service.py`

Purpose:

- HOD profile get/update helpers

### `services/library_service.py`

`get_student_library_books(db, student_email, semester)`:

- resolves student by email
- finds active `LibraryIssue` rows
- enriches with `LibraryBook` metadata

`issue_books_to_student(db, req)`:

- batch issue helper for library assignments

`upload_books_excel(db, file)`:

- Excel import for catalog population

`assign_book(db, req, admin_email)`:

- validates student and book
- reduces `available_copies`
- creates `LibraryIssue`

`return_books(db, req, admin_email)`:

- closes active issues and restores inventory count

`get_pending_books(db, srno, semester)`:

- returns unreturned issues for a student

### `services/hostel_service.py`

`upload_hostel_rooms_excel(db, file)`:

- mass-import rooms

`allocate_student_hostel(db, req, admin_email)`:

- resolves student
- validates room capacity/availability
- creates allocation
- increments occupancy

`get_student_hostel_details(db, student_email)`:

- resolves active allocation + room + derived hostel fee view

`vacate_hostel_room(db, req, admin_email)`:

- marks allocation inactive and decrements occupancy

`get_hostel_statistics(db)`:

- counts total rooms, occupied rooms, vacant capacity, active allocations

`get_all_hostel_rooms(db)` and `get_all_hostel_allocations(db)`:

- admin listing endpoints

`create_hostel_room`, `update_hostel_room`, `delete_hostel_room`:

- room CRUD helpers

`update_allocation_status(...)`:

- lets admin change status without necessarily deleting the history row

`allocate_student_to_hostel_ui(...)`:

- UI-friendly allocate path using explicit `student_id` and `room_id`

### `services/timetable_service.py`

`upload_timetable_image(...)`:

- stores uploaded timetable image in `uploads/`
- creates `TimeTable` row pointing to saved file path/URL
- this is why `/uploads` is mounted in FastAPI

### `services/notification_service.py`

Already described partly above, but the central idea is:

- notices are audience-targeted broadcasts
- filters are applied at read time based on role, branch, batch, section, or exact email

This design lets one notice target:

- all students in a branch
- one section
- one batch
- a specific faculty email
- everyone under a role

### `services/fee_structure_service.py`

`create_fee_structure(db, data)`:

- creates one fee template row

`bulk_create_fee_structure(db, items)`:

- inserts multiple templates in a loop

This service exists because fee totals are not embedded permanently in each payment row. Instead, the system derives payable fee by matching student attributes to a semester/year fee structure.

### `services/fee_compliance_service.py`

`get_fee_compliance_summary(db, batch, year)`:

- aggregates payment completion across a cohort
- useful for admin dashboards or compliance reporting

### `services/bulk_user_service.py`

`generate_password(length=8)`:

- random initial-password helper

`_apply_if_value(...)`, `_upsert_faculty_profile(...)`, `_upsert_hod_profile(...)`:

- smaller data hygiene helpers used during bulk account creation

`create_users_from_excel(db, user_data: list, role: str, same_password=True)`:

- creates only auth-layer `User` records and linked profile rows where applicable
- returns created/skipped/errors breakdown

### `services/email_service.py`

`send_password_reset_email(recipient_email, reset_link, user_name="User")`:

- builds multipart email
- connects using configured SMTP server
- logs/returns success or failure

`send_test_email(recipient_email)`:

- operational helper to validate SMTP setup

Why this file matters:

- without it, password reset becomes impossible even though tokens can still be created

### `utils/validators.py`

Contains:

- `validate_vvit_email(email)`
- `validate_email_format(email)`
- `validate_vvit_and_format(email)`

Purpose:

- centralize email policy instead of sprinkling regex checks everywhere

### `utils/academic_year.py`

Contains:

- `year_from_batch(batch)`
- `year_from_semester(semester)`
- `resolve_year(batch=None, semester=None, year=None)`

Purpose:

- unify logic where academic year can be inferred from either batch or semester

### `utils/marks_calculator.py`

This is the pure-calculation file.

Functions:

- `_to_float(value)`: safe numeric coercion
- `round2(value)`: consistent rounding helper
- `calculate_mid_marks(...)`: one mid total from its components
- `calculate_final_internal_marks(mid1, mid2)`: best/weighted internal rule
- `calculate_semester_marks(internal_marks, external_marks)`: total score
- `grade_from_percentage(percentage)`: grade letter + points
- `calc_mid_total(...)`: shorthand mid total helper
- `calc_final_internal(...)`: shorthand alias
- `grade_from_score(score)`: grade mapping helper
- `calc_sgpa(total_points, total_credits)`: SGPA formula
- `calc_cgpa(semester_rows)`: cumulative GPA formula
- `cgpa_to_percentage(cgpa)`: reporting convenience

Why this file exists:

- mathematical rules should live outside routers so they can be reused safely

### `utils/excel_reader.py`

`extract_emails(upload_file)`:

- reads account-upload sheet
- validates and deduplicates email set

`extract_academic_rows(upload_file)`:

- parses academic import rows from uploaded spreadsheets

### Schema files

Every schema file under `Backend/app/schemas/` exists for one reason: FastAPI should not accept raw untyped dictionaries when the project already knows the expected input/output shapes.

Examples:

- `schemas/auth.py`: signup/login/password-reset payloads
- `schemas/student.py`: editable student profile contract
- `schemas/faculty.py`, `schemas/hod.py`, `schemas/admin.py`: role profile contracts
- `schemas/payment.py`: payment lookup and update request contracts
- `schemas/internal_marks.py`, `schemas/external_marks.py`: exam mark payloads
- `schemas/attendance.py`: attendance create payload with per-student status items
- `schemas/hostel.py`: room create/update/allocation contracts
- `schemas/library.py`: issue/return request payloads
- `schemas/notification.py`: notification creation and display shapes
- `schemas/timetable.py`: timetable create/response contracts

What happens if schema files are removed:

- FastAPI input validation degrades
- autogenerated OpenAPI docs become weaker
- runtime type expectations become undocumented

### Other backend files

`Backend/create_tables.py`:

- small bootstrap script calling `Base.metadata.create_all(...)`
- useful in first-time local setup
- no migration history, only current schema creation

`Backend/requirements.txt`:

- Python dependency file for backend container and local installs

`Backend/Dockerfile`:

- packages backend app into a container
- installs dependencies
- exposes FastAPI service

## Level 4: Complete Data Flow

### Flow 1: Login

User action:

- user enters email, password, role on `FrontEnd/index.html`

Frontend step:

- `FrontEnd/script.js` collects values
- sends `POST /auth/login`
- content type: `application/json`

Example request:

```json
{
  "email": "student@vvit.net",
  "password": "secret",
  "role": "STUDENT"
}
```

Backend step:

1. `routers/auth.py -> signin(...)`
2. `services/auth_service.login(...)`
3. query `users`
4. verify password hash
5. generate JWT using `security.create_access_token(...)`
6. return token, email, role

Database step:

- table used: `users`

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "role": "STUDENT",
  "email": "student@vvit.net"
}
```

UI step:

- token saved in `localStorage`
- role-based redirect to `student/html/dashboard.html` or corresponding portal

### Flow 2: Student Dashboard Load

User action:

- student opens dashboard page

Frontend:

- `student/js/dashboard.js` calls `GET /student/dashboard?semester=...`
- header: `Authorization: Bearer <jwt>`

Backend logic:

1. `student.py -> get_student_dashboard_data(...)`
2. `get_current_user(...)` decodes JWT
3. find `Student` row by email
4. get most recent `Academic` row
5. compute attendance summary from attendance tables
6. compute CGPA from `SemesterGrade`
7. count library pending books
8. summarize payments
9. gather internal marks and derive ML features
10. call `predict_student_risk(...)`
11. return combined dashboard JSON

Tables touched:

- `students`
- `academics`
- `attendance_sessions`
- `attendance_records`
- `semester_grades`
- `payments`
- `library_issues`
- `internal_marks`

UI step:

- cards render attendance, CGPA, dues, and risk message

### Flow 3: Faculty Uploads Internal Marks

User action:

- faculty selects Excel file on marks page

Frontend:

- `faculty/js/marks.js` creates `FormData`
- sends `POST /faculty/internal-marks/upload`
- content type: `multipart/form-data`

Backend:

1. router validates faculty role
2. `upload_internal_marks_excel(...)` loads workbook
3. faculty profile is checked for subject identity
4. each row maps student roll number to `Student`
5. mid1 and mid2 totals computed
6. final internal computed
7. `InternalMarks` insert/update committed

Tables touched:

- `faculty`
- `students`
- `internal_marks`

Response:

- summary message with processed counts or success text

### Flow 4: Admin Uploads External Marks and Final Results Are Generated

User action:

- admin uploads semester external marks file

Frontend:

- `admin/js/results.js` sends `multipart/form-data` to `/admin/external-marks/upload/{batch}/{semester}`

Backend:

1. admin role verified
2. `upload_external_marks_excel(...)` parses rows
3. find each `Student`
4. upsert `ExternalMarks`
5. find corresponding `InternalMarks`
6. compute total semester marks
7. assign grade letter and grade points
8. upsert `CourseGrade`
9. aggregate course grades into SGPA
10. aggregate across semesters into CGPA
11. upsert `SemesterGrade`

Tables touched:

- `students`
- `external_marks`
- `internal_marks`
- `course_grades`
- `semester_grades`

Why this flow is critical:

- this is the academic heart of the ERP

### Flow 5: Student Views Result/Transcript

Frontend:

- `student/js/academic.js` calls:
  - `/student/internal-marks`
  - `/student/external-marks`
  - `/student/transcript`

Backend:

- `student_grades.py` assembles subject-level and semester-level results

Tables touched:

- `internal_marks`
- `external_marks`
- `course_grades`
- `semester_grades`

UI output:

- semester scorecards and transcript tables

### Flow 6: Attendance Marking

Frontend:

- `faculty/js/attendance.js` sends JSON payload with date, class metadata, and per-student status list

Backend:

1. `mark_attendance_api(...)`
2. `attendance_service.mark_attendance(...)`
3. create one `AttendanceSession`
4. create many `AttendanceRecord` rows for that session

Tables touched:

- `attendance_sessions`
- `attendance_records`

Later reads:

- student attendance page
- dashboard summary
- AI attendance advice
- faculty attendance reports

### Flow 7: Fee Payment Update

Two distinct flows exist:

- admin-recorded payment through admin panel
- student self-submission acknowledgement through student panel

Admin-recorded flow:

1. admin searches student via `/payments/payment/{roll_no}`
2. UI renders due categories
3. admin posts `/payments/payment/update`
4. backend inserts or updates `Payment`
5. `receipt_id` is generated and totals are recalculated on next read

Student self-submission flow:

1. student submits proof/details using `/student/payments/submit`
2. backend stores pending payment metadata
3. admin can later verify or reconcile

Tables touched:

- `payments`
- `fee_structures`
- `students`

### Flow 8: Hostel Allocation

Admin side:

1. upload rooms or create room
2. choose student and room
3. call `/admin/hostel/allocate-ui` or `/admin/hostel/allocate`
4. backend validates room capacity
5. creates `HostelAllocation`
6. increments `HostelRoom.occupied`

Student side:

- `/student/hostel` reads allocation and room details

Tables touched:

- `hostel_rooms`
- `hostel_allocations`
- `students`

### Flow 9: Library Issue and Return

Issue flow:

1. admin uploads catalog or creates issue directly
2. `/library/issue-books` or equivalent library API is called
3. backend validates available copies
4. `LibraryIssue` row created
5. `LibraryBook.available_copies` decremented

Return flow:

1. admin posts return request
2. backend marks issue as returned
3. available copies increment

Student read flow:

- `/library/student-books` shows active issues

### Flow 10: Notifications and Alerts

Broadcast notice:

1. faculty/HOD/admin posts notice JSON
2. `Notification` row created with targeting filters
3. student/faculty/HOD dashboard later reads matching notices

Direct alert:

1. faculty or HOD chooses one student
2. post alert payload
3. `Alert` row created
4. student page reads direct alerts separately

Difference:

- `Notification` is filter-based broadcast
- `Alert` is direct intervention record

### Flow 11: Timetable Upload and View

HOD:

1. uploads image through form-data
2. backend stores file under `uploads/`
3. inserts `TimeTable` row

Student/faculty:

- view portal page calling timetable endpoint
- UI uses returned URL/path to render image

## Level 5: Database Deep Dive

### Table-by-table explanation

| Table | Purpose | Key columns | Primary key | Main links |
|---|---|---|---|---|
| `users` | authentication and authorization base table | `email`, `password`, `role`, `personal_email`, `reset_token`, `is_active` | `id` | linked logically to `students.user_email`, `faculty.user_email`, `hod.email`, `admin_profiles.email` |
| `students` | student master profile | `roll_no`, `user_email`, `first_name`, `last_name`, `branch`, `section`, `batch`, `course`, `quota`, contact fields | `id` | parent identity for academics, marks, attendance, payments, hostel, library |
| `faculty` | faculty profile and assigned subject metadata | `user_email`, `first_name`, `subject_code`, `subject_name`, `branch` | `id` | used by attendance and internal marks upload |
| `hod_profiles` | HOD profile table | `email`, `branch`, personal details | `id` | governs HOD dashboard scope |
| `admin_profiles` | admin profile details | `email`, contact fields | `id` | admin self-profile |
| `academics` | per-student academic placement per semester/year | `sid`, `srno`, `user_email`, `branch`, `batch`, `course`, `year`, `semester`, `section`, `quota`, `status` | `id` | bridge between student and cohort context |
| `internal_marks` | internal/mid assessment record per student-subject-semester | `sid`, `srno`, `subject_code`, component scores, `mid1`, `mid2`, `final_internal_marks`, `semester` | `id` | consumed during result computation |
| `external_marks` | end-semester exam marks | `sid`, `srno`, `subject_code`, `external_marks`, `semester_marks`, `grade`, `credits`, `semester` | `id` | combined with internals into final result |
| `course_grades` | subject-wise final computed grade | `sid`, `semester`, `subject_code`, `subject_name`, `credits`, `total_marks`, `grade`, `grade_points`, `credit_points` | `id` | source for transcript rows |
| `semester_grades` | per-semester SGPA/CGPA aggregate | `sid`, `semester`, `sgpa`, `cgpa`, `total_credits`, `result_status` | `id` | dashboard, transcript, AI previous-SGPA feature |
| `semester_results` | older aggregate result table kept for backward compatibility | `sid`, `srno`, `rollno`, `semester`, `sgpa`, `cgpa` | `id` | legacy path, mostly superseded by `semester_grades` |
| `attendance_sessions` | one marked class occurrence | `faculty_email`, `subject_code`, `branch`, `section`, `semester`, `date`, `period` | `id` | parent row for many attendance records |
| `attendance_records` | per-student status inside one session | `session_id`, `srno`, `status`, `semester`, `date` | `id` | child rows used in summaries |
| `payments` | payment transaction or pending fee row | `receipt_id`, `srno`, `student_email`, `fee_type`, `amount_paid`, `year`, `semester`, `payment_method`, `status`, `updated_by` | `id` | matched against `fee_structures` to compute dues |
| `fee_structures` | canonical payable fee matrix | `quota`, `residence_type`, `year`, `semester`, `tuition_fee`, `bus_fee`, `hostel_fee`, `misc_fee` | `id` | determines expected dues |
| `hostel_rooms` | hostel room inventory | `room_number`, `sharing`, `room_type`, `capacity`, `occupied`, `status` | `id` | parent for allocations |
| `hostel_allocations` | room assignment history | `student_id`, `room_id`, `status`, `allocated_by`, `allocated_on` | `id` | links room and student |
| `library_books` | catalog inventory | `book_id`, `title`, `author`, `category`, `total_copies`, `available_copies` | `id` | parent for issues |
| `library_issues` | issued-book records | `book_id`, `student_id`, `semester`, `issue_date`, `return_date`, `status`, `issued_by` | `id` | active loans |
| `notifications` | filter-targeted broadcast notice | `title`, `message`, `target_role`, `target_email`, `batch`, `branch`, `section`, `created_by`, `created_at` | `id` | inbox content for multiple roles |
| `alerts` | direct student alert record | `student_roll_no`, `message`, `created_by`, `creator_role`, `created_at` | `id` | intervention history |
| `subjects` | subject catalog / metadata | fields for code/name/credits depending on actual seed usage | `id` | not strongly used in the main flows |
| `timetables` | uploaded timetable image metadata | `branch`, `semester`, `section`, `image_url`, `uploaded_by` | `id` | rendered by portals |

### Relationship explanation

Logical one-to-many relationships:

- one `User` -> one `Student` or `Faculty` or `HODProfile` or `AdminProfile`
- one `Student` -> many `Academic`
- one `Student` -> many `InternalMarks`
- one `Student` -> many `ExternalMarks`
- one `Student` -> many `CourseGrade`
- one `Student` -> many `SemesterGrade`
- one `AttendanceSession` -> many `AttendanceRecord`
- one `HostelRoom` -> many `HostelAllocation` over time
- one `Student` -> many `LibraryIssue`
- one `LibraryBook` -> many `LibraryIssue`

Important note:

- many of these are logical relationships, not SQLAlchemy `relationship()` declarations
- the code usually performs manual joins by querying matching IDs/roll numbers

### Foreign key style

The schema is mixed:

- some connections are by integer ID:
  - `Academic.sid -> Student.id`
  - `HostelAllocation.student_id -> Student.id`
  - `HostelAllocation.room_id -> HostelRoom.id`
  - `LibraryIssue.student_id -> Student.id`
- some connections are by natural keys:
  - `Payment.srno -> Student.roll_no`
  - `AttendanceRecord.srno -> Student.roll_no`
  - `Notification.target_email -> users/students/faculty`

Trade-off:

- natural keys make Excel import and admin lookup easier
- integer foreign keys are cleaner for relational integrity
- mixing both creates extra complexity

### How APIs connect to tables

- `/auth/*` -> `users`
- `/student/profile` -> `students`
- `/student/dashboard` -> `students`, `academics`, `semester_grades`, `payments`, `library_issues`, attendance tables, mark tables
- `/faculty/internal-marks/*` -> `faculty`, `students`, `internal_marks`
- `/admin/external-marks/upload/*` -> `students`, `internal_marks`, `external_marks`, `course_grades`, `semester_grades`
- `/payments/*` -> `payments`, `fee_structures`, `students`
- `/library/*` -> `library_books`, `library_issues`, `students`
- `/admin/hostel/*` and `/student/hostel` -> `hostel_rooms`, `hostel_allocations`, `students`
- `/notifications` style endpoints -> `notifications`, `alerts`
- `/ai/*` -> mark tables, `semester_grades`, attendance tables, `academics`, `students`

## Level 6: Architecture

### Identified architecture type

This project is best described as:

- layered monolith
- role-based ERP web application
- static frontend + REST backend + relational database

It is not:

- microservices
- event-driven distributed system
- classical MVC server-rendered app

### Frontend layer

Characteristics:

- plain HTML/CSS/JavaScript multi-page application
- each role has a dedicated folder and page set
- state is mostly:
  - in DOM
  - in `localStorage`
  - in per-page JavaScript variables

Responsibilities:

- collect form input
- send fetch requests
- render returned JSON into tables/cards/modals
- store token and redirect by role

### Backend layer

Sub-layers:

- router layer: HTTP path definitions and role checks
- schema layer: request/response validation
- service layer: business logic and data transformation
- model layer: database schema mapping
- utility layer: shared calculations and parsing helpers

Why this layering exists:

- routers stay thin
- services remain reusable
- calculations and parsing can be reused by multiple routes

### Database layer

MySQL stores:

- transactional ERP data
- academic records
- financial records
- hostel/library operations
- notification history

The ORM layer is SQLAlchemy declarative models, but relationship navigation is mostly manual rather than declarative.

### Internal communication

Communication path inside backend usually follows:

`router -> dependency auth -> service -> model queries -> commit/return`

Example:

`faculty/js/marks.js -> POST /faculty/internal-marks/upload -> routers/faculty.py -> services/excel_marks_service.py -> models/internal_marks.py + models/student.py`

## Level 7: Deployment and DevOps

### Local development flow

Backend:

1. install Python dependencies from `Backend/requirements.txt`
2. configure `.env`
3. start MySQL
4. run `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

Frontend:

- static files can be opened directly or served by a simple HTTP server
- pages call backend directly by URL

### Docker flow

`docker-compose.yml` defines three services:

- `mysql`
- `backend`
- `frontend`

Expected build/run chain:

1. MySQL container starts
2. backend container waits for MySQL health
3. backend uses `DATABASE_URL=mysql+pymysql://root:root@mysql:3306/erp_db`
4. frontend container serves static files through Nginx on port `80`

### Dockerfile roles

`Backend/Dockerfile`:

- copies backend source
- installs Python requirements
- launches FastAPI server

`docker/Dockerfile.frontend`:

- packages static frontend into Nginx image

### Environment variables

Runtime code expects:

- `DATABASE_URL`
- `JWT_SECRET`
- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SENDER_EMAIL`
- `PASSWORD_RESET_BASE_URL`
- `GEMINI_API_KEY`

### Important configuration mismatches

These are worth mentioning in review or viva because they show deep repository understanding:

1. `.env.example` uses `SECRET_KEY`, while runtime code reads `JWT_SECRET`.
2. `.env.example` uses `SENDER_PASSWORD`, while runtime code reads `SMTP_PASSWORD`.
3. README says Docker UI is on `http://localhost:8080`, but `docker-compose.yml` publishes `80:80`.
4. `docker-compose.yml` contains a duplicated/malformed section in the MySQL service, repeating `MYSQL_DATABASE`, `ports`, `volumes`, and `healthcheck`.

### CI/CD

There is no implemented CI/CD pipeline in the repository:

- no `.github/workflows`
- no Jenkinsfile
- no GitLab CI

So deployment is manual:

- build images
- run Compose
- configure environment variables externally

## Level 8: Connection Mapping

### Frontend page to backend to database mappings

`FrontEnd/index.html`

- calls -> `FrontEnd/script.js`
- sends -> `/auth/login`
- uses -> `routers/auth.py`
- calls -> `services/auth_service.py`
- queries -> `users`

`student/html/dashboard.html`

- loads -> `student/js/main.js`
- loads -> `student/js/dashboard.js`
- calls -> `/student/dashboard`
- uses -> `routers/student.py`
- queries -> `students`, `academics`, `payments`, `semester_grades`, `attendance_sessions`, `attendance_records`, `library_issues`, `internal_marks`
- calls -> `services/inference.py`

`student/html/academic.html`

- calls -> `student/js/academic.js`
- calls -> `/student/internal-marks`, `/student/external-marks`, `/student/transcript`
- uses -> `routers/student.py` and `routers/student_grades.py`
- queries -> `internal_marks`, `external_marks`, `course_grades`, `semester_grades`

`student/html/attendance.html`

- calls -> `student/js/attendance.js`
- hits -> `/student/attendance/*`
- uses -> `attendance_service.py`
- queries -> `attendance_sessions`, `attendance_records`

`student/html/fees.html`

- calls -> `student/js/fees.js`
- hits -> `/student/payments`
- router -> `student.py`
- service -> `payment_service.py`
- tables -> `payments`, `fee_structures`, `students`

`faculty/html/marks.html`

- calls -> `faculty/js/marks.js`
- hits -> `/faculty/internal-marks/upload`, `/faculty/internal-marks/get`, `/faculty/internal-marks/update`
- router -> `faculty.py`
- services -> `excel_marks_service.py`, `internal_marks_service.py`
- tables -> `faculty`, `students`, `internal_marks`

`faculty/html/attendance.html`

- calls -> `faculty/js/attendance.js`
- hits -> `/faculty/class-students`, `/faculty/attendance/mark`, `/faculty/attendance/view`
- router -> `faculty.py`
- service -> `attendance_service.py`
- tables -> `students`, `academics`, `attendance_sessions`, `attendance_records`

`faculty/html/students.html`

- calls -> `faculty/js/students.js`
- hits -> `/faculty/student-list`, `/ai/aews/student-risk/{roll_no}`, `/faculty/alerts/send`
- routers -> `faculty.py`, `ai_route.py`
- services -> `faculty_service.py`, `inference.py`, notification/alert logic
- tables -> `students`, `academics`, `payments`, `semester_grades`, marks tables, `alerts`

`hod/html/students.html`

- calls -> `hod/js/students.js`
- hits -> `/hod/students-analytics`, `/hod/student/{roll_no}`
- router -> `hod.py`
- tables -> `students`, `academics`, `semester_grades`, attendance/payment data for analytics

`admin/html/admissions.html`

- calls -> `admin/js/admissions.js`
- hits -> `/admin/upload-students`
- router -> `admin.py`
- service -> `excel_service.py`
- tables -> `users`, `students`, `academics`, `payments`, `faculty`, `hod_profiles`

`admin/html/results.html`

- calls -> `admin/js/results.js`
- hits -> `/admin/external-marks/upload/{batch}/{semester}`
- service -> `excel_marks_service.py`
- tables -> `external_marks`, `course_grades`, `semester_grades`, `internal_marks`

`admin/html/hostel-new.html`

- calls -> `admin/js/hostel-new.js`
- hits -> multiple `/admin/hostel/*`
- router -> `admin.py`
- service -> `hostel_service.py`
- tables -> `hostel_rooms`, `hostel_allocations`, `students`

`admin/html/library.html`

- calls -> `admin/js/library.js`
- hits -> `/library/*`
- router -> `library.py`
- service -> `library_service.py`
- tables -> `library_books`, `library_issues`, `students`

### Backend dependency graph in words

The deepest reusable chain in the project is:

1. `main.py` wires routers.
2. each router imports `get_current_user` and `SessionLocal` or `get_db`.
3. routers import schema classes for request typing.
4. routers call service functions.
5. services import models and sometimes utilities.
6. models all depend on `core/database.Base`.
7. security-sensitive flows additionally depend on `security.py`.
8. AI flows additionally depend on:
   - `services/inference.py`
   - `services/ai_service.py`
   - saved model artifacts under `ml_models/`

## Level 9: Why Major Components Exist

### Why FastAPI

Chosen because:

- quick REST development
- automatic validation through Pydantic
- built-in docs at `/docs`
- good fit for JSON-heavy ERP APIs

Alternatives:

- Django REST Framework: stronger batteries-included admin and ORM ecosystem
- Express.js: more flexible JavaScript stack but less typed by default

Trade-off:

- FastAPI is concise, but this repo still requires careful structuring because plain SQLAlchemy + many manual joins can become messy

### Why static HTML/CSS/JS frontend

Chosen because:

- easy to build in an academic setting
- no build pipeline required
- deployable through simple Nginx static hosting

Alternatives:

- React/Vue/Angular SPA

Trade-offs:

- current approach is simple and approachable
- but repeated code across role folders reduces reuse and maintainability

### Why MySQL

Chosen because:

- structured relational data dominates ERP workloads
- familiar in academic environments
- transactional consistency matters for fees, attendance, and results

Alternative:

- PostgreSQL would offer stronger advanced SQL features and often better JSON/query power

### Why Excel imports

Because colleges often already maintain records in spreadsheets.

Alternative:

- direct admin form entry or CSV-only pipelines

Trade-off:

- Excel support matches real admin habits
- but spreadsheet formats introduce header inconsistencies and dirty data handling complexity

### Why XGBoost + SHAP

Chosen because:

- tabular academic data is a strong fit for gradient-boosted trees
- SHAP provides per-feature explanation, which is better than opaque risk scores

Alternative:

- logistic regression for simpler interpretability
- neural networks for more complexity but less explainability

Trade-off:

- XGBoost is performant and accurate on tabular data
- model management still needs versioning and retraining discipline

### Why layered monolith instead of microservices

Because:

- the team likely needed fast delivery
- domain boundaries are present but not independently scaled
- academic ERP traffic usually does not justify service sprawl initially

Trade-off:

- monolith is simpler to deploy
- but growing feature count increases coupling risk

## Level 10: Edge Cases, Validation, Security, Performance, and Review Findings

### Validation behavior

Good validation patterns:

- schema-based request validation with Pydantic
- role checks through JWT dependency
- email pattern validation helpers
- spreadsheet duplicate detection in some import flows
- marks clamping in AI feature generation

Validation gaps:

- many query parameters are accepted without strict enums
- some endpoints rely on convention rather than DB constraints
- not all files use centralized validation consistently

### Error handling

Positive points:

- routers often wrap permission issues with `HTTPException`
- Excel services use rollback on failure
- password reset flow handles invalid token cases

Weak points:

- some service functions return plain dictionaries instead of raising typed exceptions
- some routes can return mixed response shapes, which makes frontend handling less predictable

### Security analysis

Implemented:

- password hashing with bcrypt/passlib
- JWT-based auth
- role-based access checks in routers
- SMTP tokenized reset flow

Risks:

1. JWT token in `localStorage`
   - vulnerable to XSS-based token theft
2. permissive CORS in `main.py`
   - convenient for dev, weaker for production hardening
3. default secrets in config
   - runtime defaults should not be production-safe values
4. some routes duplicate access logic rather than centralizing role guards
5. no rate limiting on login/reset endpoints

### Performance analysis

Fine for small-to-medium college workloads:

- MySQL + FastAPI is enough
- static frontend is lightweight

Potential bottlenecks:

- repeated per-student query loops in dashboards/analytics
- manual joins can create N+1 query patterns
- Excel imports are synchronous and block request thread
- AI and SHAP inference may add latency for dashboard-heavy batches

### Scalability considerations

Ways this could scale:

- add background jobs for Excel processing and email sending
- cache heavy dashboard summaries
- add DB indexes on roll number, email, semester, subject code
- normalize subject catalog usage
- introduce Alembic migrations
- split AI inference as separate worker service only if needed

### Code review findings

These are concrete repository findings, not generic advice.

1. Duplicate code in `Backend/app/routers/student.py`
   - the file contains duplicated import blocks and repeated router setup, which increases maintenance risk and can confuse future merges.

2. Legacy or dead code in `Backend/app/core/__init__.py`
   - this file contains duplicate security-related definitions and appears to include commented or repeated code rather than being the authoritative security module.

3. Router duplication in `Backend/app/routers/__init__.py`
   - it implements student-grade routes while the project also has `student_grades.py`, suggesting route evolution without cleanup.

4. Config drift between docs and runtime
   - `.env.example` and runtime config variable names do not fully match.
   - README Docker port documentation does not match current Compose file.

5. Compose file hygiene issue
   - `docker-compose.yml` has duplicated MySQL keys inside the service definition, which should be cleaned before production use.

6. Payment model usage inconsistency
   - some faculty aggregation code tries to read a non-guaranteed `amount` attribute from payment rows, while actual recorded paid value is `amount_paid`.

7. Schema evolution drift
   - both `semester_results` and `semester_grades` exist, which suggests partial migration from an older result model to a newer one.

8. Missing automated tests
   - there is no real unit/integration test suite for auth, marks calculation, imports, or attendance rules.

### Suggested improvements

- replace `localStorage` auth with httpOnly cookies or refresh-token architecture
- standardize all env variable names
- remove duplicate/legacy router and core files
- add Alembic migrations
- add tests for marks, fees, attendance, and auth
- add SQLAlchemy relationships or a repository/query layer
- move long-running imports to background tasks

## Level 11: Interview and Viva Questions

### 20 basic questions with answers

1. What is this project?
   Answer: It is a college ERP system that manages student, faculty, HOD, and admin workflows such as attendance, marks, fees, hostel, library, notifications, timetable, and academic risk prediction.
2. Which users use the system?
   Answer: Admin, HOD, Faculty, and Student.
3. What backend framework is used?
   Answer: FastAPI.
4. What database is used?
   Answer: MySQL through SQLAlchemy ORM models.
5. How does login work?
   Answer: Credentials are verified against the `users` table, a JWT token is generated, and the frontend stores it for subsequent authorized API calls.
6. How is role-based access enforced?
   Answer: The JWT contains user identity and role, and routers check `user["role"]` after decoding through `get_current_user`.
7. Where are student details stored?
   Answer: In the `students` table.
8. Where are faculty details stored?
   Answer: In the `faculty` table.
9. How are academic details stored?
   Answer: In the `academics` table, which tracks batch, branch, year, semester, section, quota, and status.
10. How are internal marks stored?
    Answer: In the `internal_marks` table.
11. How are external marks stored?
    Answer: In the `external_marks` table.
12. How is SGPA stored?
    Answer: In the `semester_grades` table after aggregation from subject-wise course grades.
13. What is the purpose of `course_grades`?
    Answer: It stores final subject-level grade results, including grade points and credit points.
14. How is attendance marked?
    Answer: Faculty create one attendance session and many attendance records, one per student.
15. What is the difference between notification and alert?
    Answer: A notification is a broadcast message filtered by role/cohort, while an alert is a direct message to a particular student.
16. How are hostel rooms managed?
    Answer: Through `hostel_rooms` and `hostel_allocations` tables plus admin CRUD endpoints.
17. How are library books managed?
    Answer: Catalog entries live in `library_books`, and issued-book records live in `library_issues`.
18. Why is Excel upload used?
    Answer: Because college administration often already maintains data in spreadsheets, so Excel import matches real operational workflows.
19. What AI feature exists in the project?
    Answer: Student academic risk prediction using an XGBoost model and attendance advice using Gemini.
20. Is this project microservices-based?
    Answer: No, it is a layered monolith.

### 20 intermediate questions with answers

1. Why are `users` and `students` separate tables?
   Answer: `users` stores authentication and authorization data, while `students` stores domain-specific profile information. This separation prevents business profile changes from interfering with login logic.
2. How does internal marks calculation happen?
   Answer: Component scores such as objective, descriptive, open-book, and seminar are read from Excel, normalized, converted into `mid1` and `mid2`, and then combined into `final_internal_marks`.
3. How are semester results generated?
   Answer: Admin uploads external marks, which are combined with internal marks to compute total score, grade letter, grade points, course-level grades, and finally SGPA/CGPA aggregates.
4. Why are there both `course_grades` and `semester_grades` tables?
   Answer: `course_grades` stores subject-level results, while `semester_grades` stores semester-level aggregate metrics like SGPA and CGPA.
5. How does the student dashboard get CGPA?
   Answer: It reads aggregated semester rows from `semester_grades` and computes or returns the latest CGPA.
6. How does the system identify which notifications a student should see?
   Answer: It matches the student’s email, batch, branch, section, and role against targeting filters stored in the `notifications` table.
7. How is fee due calculated?
   Answer: Paid amounts come from `payments`, but payable expectations come from `fee_structures` based on quota, residence type, year, and semester.
8. What is the purpose of `academics.sid`?
   Answer: It links the academic placement row back to the student’s integer primary key.
9. Why is `roll_no` still used across many queries?
   Answer: Roll number is a natural identifier already used in institutional records and spreadsheets, so it simplifies imports and human lookup.
10. What happens when attendance is marked?
    Answer: One session row is created for the class occurrence, then per-student statuses are inserted into attendance records.
11. How is hostel occupancy controlled?
    Answer: Allocation logic checks room capacity and updates occupied count whenever a student is allocated or vacated.
12. How does password reset work?
    Answer: The backend generates a reset token, stores it on the user record, emails a reset link, then validates token and email before updating the hashed password.
13. Why are routers and services separated?
    Answer: Routers handle HTTP and access control, while services contain reusable business logic and database operations.
14. Why are Pydantic schemas important here?
    Answer: They validate incoming requests, document endpoint contracts, and prevent arbitrary loosely-typed payload handling.
15. How does faculty risk prediction work?
    Answer: The system builds a feature vector using mid marks, attendance percentage, previous SGPA, and backlog count, then feeds it into the saved ML model.
16. What is SHAP used for?
    Answer: It explains which features influenced the academic-risk prediction.
17. Why is the frontend split by role folders?
    Answer: Each role sees different pages and workflows, so role-specific folders keep navigation and UI separated.
18. Why does the system use static pages instead of a SPA framework?
    Answer: It simplifies deployment and development, though it increases duplication.
19. Where is timetable data stored?
    Answer: In the `timetables` table, with images stored on disk under `uploads/`.
20. What is one weakness of the current schema design?
    Answer: It mixes integer foreign keys and natural keys like roll number, which complicates consistency and query design.

### 20 advanced questions with answers

1. What architectural style best describes this codebase?
   Answer: A layered monolith with domain-organized routers and services, backed by a relational database and a static multi-page frontend.
2. Why is this not strict MVC?
   Answer: The backend does not render templates or serve views as controllers in the classic MVC sense; instead, it exposes REST APIs and the frontend renders separately.
3. What technical debt do you see in route organization?
   Answer: There is duplication between `student_grades.py` and `routers/__init__.py`, and `student.py` contains repeated import/router sections, indicating incomplete cleanup after refactors.
4. What technical debt do you see in configuration?
   Answer: Documentation and runtime environment variable names drift apart, and Docker port documentation does not match the current compose file.
5. How would you improve database integrity?
   Answer: Add explicit foreign keys where missing, standardize on integer references, add indexes, and create Alembic migrations for schema evolution.
6. How would you reduce N+1 query risk?
   Answer: Consolidate analytics and dashboard queries with joins, grouped aggregates, or repository-level optimized query functions instead of row-wise loops.
7. How would you productionize Excel imports?
   Answer: Move them to background jobs, validate schema upfront, store import audit logs, and report row-level errors in a structured way.
8. How would you improve security of tokens?
   Answer: Replace localStorage bearer tokens with short-lived access tokens plus refresh tokens in httpOnly secure cookies.
9. What does the AI subsystem actually do in the shipped code?
   Answer: It performs local academic-risk prediction using saved model artifacts and generates Gemini-based attendance advice; it is not a full retrieval-augmented AI architecture.
10. Why is SHAP valuable in this context?
    Answer: Because academic-risk outputs affect intervention decisions, and stakeholders need interpretable reasons rather than a raw score.
11. What challenge exists in fee handling?
    Answer: `Payment` stores transaction progress, but expected total fee comes from `FeeStructure`, so fee computation depends on correctly matching student context and structure rows.
12. Why might `semester_results` and `semester_grades` coexist?
    Answer: It suggests a schema transition where older code stored only aggregate semester results, and newer code introduced a richer grade model but did not fully remove the legacy table.
13. How would you modularize this monolith if scale increased?
    Answer: First separate query/service boundaries cleanly, then carve domains like auth, academics, finance, and hostel/library into bounded modules or services only when operational scale requires it.
14. What is a design trade-off of manual joins versus SQLAlchemy relationships?
    Answer: Manual joins give direct control and can feel simpler for newcomers, but they duplicate logic and reduce model expressiveness and maintainability.
15. Where do you see hidden coupling between modules?
    Answer: Dashboard and analytics routes often directly understand multiple table shapes, AI feature construction depends on grade and attendance storage details, and imports assume specific Excel column conventions.
16. How would you add observability?
    Answer: Add structured logging, request IDs, import audit tables, background-job logs, and metrics on login failures, import durations, and API latency.
17. What is the biggest operational risk in the current deployment setup?
    Answer: Manual environment management plus documentation/config drift can cause inconsistent deployments, especially around secrets, ports, and email settings.
18. How would you test the marks pipeline?
    Answer: Write deterministic unit tests for calculation helpers, service-level tests for internal/external upload parsing, and end-to-end tests verifying SGPA/CGPA outputs for known sample data.
19. How would you make the notification system more robust?
    Answer: Normalize targeting rules, add read/unread state, and possibly introduce message audit trails or scheduling.
20. If asked for the project’s strongest technical feature, what would you say?
    Answer: The strongest feature is the integration of operational ERP workflows with explainable academic-risk prediction, because it connects daily administration with proactive student intervention.

## Level 12: Presentation Mode

### 2-minute explanation

This project is a role-based college ERP system built using a static HTML/CSS/JavaScript frontend, a FastAPI backend, and a MySQL database. It supports four major users: admin, HOD, faculty, and student. Admin manages onboarding, fee structures, hostel rooms, external marks uploads, and notifications. Faculty manage attendance, internal marks, and student interventions. HOD monitors department-wide student analytics, faculty details, notifications, and timetables. Students can view their profile, academics, attendance, fees, hostel allocation, library books, notifications, and alerts.

Architecturally, it is a layered monolith. The frontend sends REST API calls using JWT authentication. The backend routes validate the token, invoke service-layer business logic, and read or write SQLAlchemy models backed by MySQL. One special feature is the Academic Early Warning System, where student attendance, mid marks, previous SGPA, and backlog data are used to predict academic risk using an XGBoost model with SHAP-based explanation, while Gemini generates attendance advice for students with low attendance.

### 5-minute explanation

This project solves a very practical problem in colleges: most academic and administrative workflows are scattered across spreadsheets, manual registers, and separate systems. This ERP centralizes those workflows into one application with role-based access for admin, HOD, faculty, and students.

At the frontend level, the project uses static role-specific portals. Each page has its own JavaScript file that calls REST APIs with `fetch`, sends JWT in the authorization header, and renders JSON responses directly into the UI. This keeps deployment simple because the frontend can be served as static files through Nginx.

At the backend level, FastAPI is used in a layered structure. Routers define endpoints and role checks, schemas validate request and response payloads, services hold business logic, and SQLAlchemy models map database tables. For example, faculty attendance marking creates one attendance session and many attendance records. Internal marks uploads parse Excel sheets and calculate mid totals and final internal marks. External marks uploads are even more important because they combine with internal marks to compute course grades, semester SGPA, and cumulative CGPA.

Database design is strongly domain-driven. There are separate tables for users, students, faculty, HOD profiles, academics, internal marks, external marks, course grades, semester grades, payments, fee structures, hostel rooms, hostel allocations, library books, library issues, notifications, alerts, and timetables. So the data model covers both academic and operational modules.

The project also includes an AI layer. For students, the system can analyze low-attendance subjects and generate advice using Gemini. For faculty, it can predict academic risk for a student using attendance, internals, previous SGPA, and backlog count. This uses saved XGBoost model artifacts and returns both a risk level and an explanation.

From a design perspective, the project is strong because it connects real college workflows to analytics and intervention. From a review perspective, there is some technical debt: duplicated routes, no automated tests, no migration tool, a few config mismatches, and some schema evolution drift. But as an end-to-end academic ERP with AI integration, it is substantial and presentation-worthy.

### 10-minute deep explanation

This project is a comprehensive Smart College ERP with academic-risk intelligence added on top. The main problem it solves is institutional fragmentation. In many colleges, admissions data, fees, attendance, marks, hostel records, library issue logs, and student communication are stored separately, often in spreadsheets. That creates duplication, delayed reporting, and weak intervention capability. This system centralizes those processes in a single role-based application.

There are four users. Admin handles onboarding, fee structures, hostels, library, results upload, dashboard statistics, and institution-wide communication. HOD manages department-level oversight, including faculty visibility, student analytics, timetable publishing, and targeted alerts. Faculty manage internal marks, attendance, notifications, and direct alerts to students. Students consume their own academic and operational data through a personal dashboard.

The frontend is intentionally lightweight. It uses plain HTML, CSS, and JavaScript organized by role. Each page has a page-specific script, and shared headers and sidebars are loaded from component files. Authentication happens on the login page, which stores a JWT token in localStorage and redirects users to the correct role dashboard. Every secure page reads that token and sends it in the `Authorization` header.

The backend is implemented in FastAPI as a layered monolith. `main.py` registers all routers and configures CORS and static upload serving. The core layer handles database sessions, environment configuration, password hashing, JWT generation, and token decoding. Models define the database tables. Schemas define request and response contracts. Routers expose domain APIs. Services handle business logic such as Excel parsing, attendance aggregation, fee computation, hostel allocation, notification targeting, and result generation.

The academic pipeline is the most important internal workflow. Faculty upload internal marks from Excel. The backend parses subject-wise records and computes mid1, mid2, and final internal marks. Admin then uploads external exam marks. The backend matches those rows to students and internal marks, calculates total score, derives grade and grade points, creates subject-level course grades, and then aggregates them into semester-level SGPA and CGPA. These results power the student academic page, transcript view, dashboard summary, and the AI risk model.

Attendance is modeled in two layers. An attendance session captures one class event, such as a subject, date, period, branch, and section. Attendance records store each student’s status inside that session. This allows semester summary, subject-wise percentage, monthly views, and low-attendance detection.

Fees are handled through both a transaction table and a fee-structure table. `FeeStructure` stores what should be paid based on quota, residence type, year, and semester. `Payment` stores what has actually been paid or marked pending. The student and admin payment views combine both sides to show dues and receipts.

The hostel and library modules are also transactional. Hostel rooms maintain capacity and occupancy, while hostel allocations track assignments over time. Library books store inventory, while library issues track book loans and returns. Notifications are broadcast messages with targeting fields like role, branch, batch, and section. Alerts are direct messages to specific students.

The AI module adds value beyond standard ERP. A student-facing endpoint checks low-attendance subjects and calls Gemini to produce attendance advice. A faculty-facing endpoint builds a tabular feature vector using attendance percentage, average mid performance, previous SGPA, and backlog count, then runs a saved XGBoost model. SHAP explanations are used so the prediction is not just a black-box number.

From a software architecture point of view, the system is solid as a layered monolith, but it also shows evolution over time. There are duplicated routes, a legacy `semester_results` table next to the newer `semester_grades`, missing automated tests, and configuration mismatches between docs and runtime. If I were extending it, I would add Alembic migrations, a test suite, stricter role guard abstractions, background workers for long-running imports and email, and stronger production security for token handling. Even with those gaps, the project demonstrates full-stack ERP design, business-rule implementation, and applied AI integration in a meaningful institutional domain.
