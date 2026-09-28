# Bhumi Praman
### Intelligent Land Record Digitization &amp; Validation System
**Smart India Hackathon 2026 &middot; Problem Statement 26018** (Ministry of Rural Development) &middot; Student prototype

**Bhumi** = land, **Praman** = proof / verification.

Bhumi Praman turns scanned and legacy land records (Record of Rights / Khatauni documents) into structured,
searchable, validated digital records &mdash; using AI/OCR to do the first pass, and a human officer to make
every field official. No field is ever treated as final without a person reviewing it.

> **This is a hackathon prototype**, not a deployed government system. It uses fictional, synthetically
> generated sample data, and every accuracy figure it displays is measured live against a small labelled
> sample set &mdash; never a hard-coded claim. See [Limitations](#limitations) below.

---

## 1. Project Overview

The system takes a scanned/photographed land document (PDF, JPG, or PNG), runs it through an OCR + field
extraction pipeline, scores every extracted field's confidence, checks it for validation issues and possible
duplicates/ownership conflicts, and routes it to a Verification Officer who corrects, accepts, or rejects each
field before the record is saved as an official, searchable, mapped, and auditable digital record.

## 2. Problem Statement

PS 26018 asks for a system that digitizes India's legacy land records (often handwritten or degraded
scans, in multiple languages, spread across village/tehsil/district revenue offices) into a structured,
searchable, validated digital archive &mdash; while keeping the process auditable and keeping trained officers
in the loop rather than fully automating a legally sensitive decision.

## 3. Features

- Multilingual OCR (English, Hindi, Bengali, Assamese and etc) with image preprocessing (deskew, denoise, contrast, binarize)
- Rule-based structured field extraction across 12 Record-of-Rights fields, each with a transparent confidence score
- Real source highlighting &mdash; extracted field values are matched back to their location on the original
  scan via OCR bounding boxes, not simulated
- Validation engine: required-field/format checks, possible-duplicate detection, possible ownership-conflict detection
- Human verification workspace: side-by-side document + extracted fields, accept/edit/reject per field
- Role-based access control (Administrator / Verification Officer / Record Officer), enforced server-side
- Full audit trail of every upload, edit, verification, rejection, and report generation
- Search &amp; archive registry across all digitized records
- GIS explorer (Leaflet + OpenStreetMap), clearly labelled as prototype/demonstration positioning
- Dashboard analytics, including a live, real evaluation re-run against a ground-truth sample set
- Official PDF report export per verified record, with a SHA-256 record integrity hash

## 4. Architecture

```
Browser (React)
   |
   v
FastAPI backend  <----> SQLite/PostgreSQL database
   |
   v
AI Prototype Adapter (backend/app/services/pipeline_service.py)
   |
   v
ai/  --  preprocessing -> OCR -> field extraction -> confidence scoring -> validation
   |
   v
Local file storage (storage/uploads, processed, reports)
```

The browser never touches Python directly. Every AI call goes through the FastAPI backend, which calls a
single adapter module (`pipeline_service.py`) that wraps the `ai/` package &mdash; so the OCR/AI engine can be
swapped later without touching the API or frontend.

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS v4 + React Router + TanStack Query + Recharts + react-leaflet |
| Backend | Python + FastAPI + SQLAlchemy 2.0 + Pydantic v2 |
| AI / OCR | OpenCV, Tesseract (via pytesseract), rule-based extraction, PyMuPDF (PDF handling) |
| Database | SQLite for local development (zero setup); swappable to PostgreSQL via `DATABASE_URL` |
| Auth | JWT (PyJWT) + bcrypt |
| Reports | ReportLab (PDF generation) |
| Testing | pytest, httpx, FastAPI TestClient |

## 6. Folder Structure

```
bhumi-praman/
├── frontend/        React + Vite + TypeScript app
├── backend/         FastAPI app (app/api, models, schemas, services, database)
├── ai/              The Crystal OCR/extraction pipeline (see ai/README.md)
├── data/            Sample documents + ground truth (safe, fictional demo data)
├── database/seed/   Seed script — demo users + real sample documents
├── storage/         Uploaded files, processed pages, generated PDF reports
├── deployment/       Docker files
└── README.md        This file
```

## 7. Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Tesseract OCR** (with English, Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu. language data)
- Git

## 8–9. Installation &amp; Environment Setup

### Windows (PowerShell) &mdash; primary supported dev environment

**1. Install Tesseract OCR:**
Download and run the UB Mannheim Windows installer: https://github.com/UB-Mannheim/tesseract/wiki
During install, tick **Additional language data** and select **Hindi** and **Assamese** (if Assamese isn't
listed in your installer version, download `asm.traineddata` from
https://github.com/tesseract-ocr/tessdata and place it in `tessdata\` under your Tesseract install folder).

By default Tesseract installs to `C:\Program Files\Tesseract-OCR` and is **not** added to PATH. You have two options:
- Add `C:\Program Files\Tesseract-OCR` to your PATH, **or**
- Set `TESSERACT_CMD` in `.env` (see below) to `C:\Program Files\Tesseract-OCR\tesseract.exe`

**2. Clone and set up the backend:**
```powershell
git clone <your-repo-url>
cd bhumi-praman
copy .env.example .env
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If `Activate.ps1` is blocked, see [Troubleshooting](#troubleshooting--common-errors) below.

**3. Seed the database (creates demo users + processes the 3 real sample documents):**
```powershell
python ..\database\seed\seed.py
```

**4. Set up the frontend (new terminal tab):**
```powershell
cd bhumi-praman\frontend
npm install
```

### macOS / Linux

```bash
brew install tesseract tesseract-lang   # macOS
# or: sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-asm   # Debian/Ubuntu

git clone <your-repo-url>
cd bhumi-praman
cp .env.example .env
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ../database/seed/seed.py

cd ../frontend
npm install
```

## 10. Database Setup

No separate step needed for local development &mdash; SQLite is used by default, and the seed script creates
the file and all tables automatically (`backend/bhumi_praman.db`, git-ignored). For a real deployment, set
`DATABASE_URL` in `.env` to a PostgreSQL connection string (e.g.
`postgresql+psycopg://user:pass@host:5432/bhumi_praman`); every query goes through SQLAlchemy, so this is a
config change, not a code change.

## 11. AI/OCR Setup

Already covered in step 1 above. To verify Tesseract is correctly installed:
```powershell
tesseract --list-langs
```
You should see `eng`, `hin`, and `asm` in the list.

## 12–14. Running the Application

**Backend** (from `backend/`, venv active):
```powershell
python -m uvicorn app.main:app --reload --port 8000
```
API docs auto-generated at http://localhost:8000/docs

**Frontend** (from `frontend/`, separate terminal):
```powershell
npm run dev
```
Open http://localhost:5173 &mdash; the dev server proxies `/api/*` to the backend automatically, so both need
to be running together but there's nothing else to configure.

For frontend deployed part you can visit https://bhumi-praman.vercel.app

**One-command option:** `scripts/start-dev.ps1` (Windows) starts both servers in one PowerShell window &mdash;
see that script's comments for what it does.

## 15. Sample Credentials

Created by the seed script:

| Role | Employee Code | Password |
|---|---|---|
| Administrator | `ADM-0001` | `Admin@123` |
| Verification Officer | `OFC-KAM-1102` | `Officer@123` |
| Record Officer | `REC-0007` | `Record@123` |

The login screen also has one-click "quick demo sign-in" cards that fill these in &mdash; they don't grant
access themselves, they just save typing; the server always determines the actual role from the account.

## 16. Sample Document Usage

The seed script processes the three real sample documents in `data/sample_documents/` (`DOC001.png`,
`DOC002.png`, `DOC003.png` &mdash; clean, medium-degraded, and heavily-degraded scans of the same fictional
Record-of-Rights template) through the real pipeline, so the app has realistic data immediately. To try the
upload flow yourself with a fresh document, any of these three PNGs can be re-uploaded through **Bulk
Ingestion**, or generate new synthetic samples with `python ai/generate_samples.py`.

## 17. API Documentation

FastAPI generates interactive OpenAPI docs automatically:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 18. Testing

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests\test_api.py -v            # API integration tests (real pipeline, temp DB)
pytest ..\ai\tests\test_pipeline_smoke.py -v   # AI-layer unit/smoke tests
```
20 tests total, all passing as of this build: field extraction, confidence scoring, the field&rarr;source-location
matcher, duplicate/conflict detection (including a regression test for a bug found and fixed during
integration &mdash; see `ai/validator.py`'s comments), the full upload&rarr;process&rarr;verify&rarr;report path,
RBAC enforcement, and the live evaluation endpoint.

Frontend: `cd frontend && npm run build` runs the TypeScript compiler and production build (no separate test
suite yet &mdash; see [Future Scope](#future-scope)).

## 19–20. Troubleshooting &amp; Common Errors

**Python not recognized** &mdash; Python isn't on PATH. Reinstall from python.org and tick "Add Python to
PATH" during setup, or use the Microsoft Store Python. Verify with `python --version`.

**Node not recognized** &mdash; Install from nodejs.org (LTS). Verify with `node --version`.

**npm dependency error** &mdash; delete `frontend\node_modules` and `frontend\package-lock.json`, then
`npm install` again.

**Port already in use** &mdash; find and stop the process:
```powershell
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```
(use `:5173` for the frontend port)

**Database connection failure** &mdash; check `DATABASE_URL` in `.env`. For SQLite (the default), make sure
the `backend/` folder is writable. For PostgreSQL, confirm the server is running and the credentials are correct.

**OCR model missing / "tesseract is not installed or it's not in your PATH"** &mdash; see section 11 above;
either add Tesseract to PATH or set `TESSERACT_CMD` in `.env` to the full path of `tesseract.exe`.

**File upload failure** &mdash; only PDF, JPG, and PNG are accepted, up to 50MB (`MAX_UPLOAD_SIZE_MB` in
`.env`). Check the backend terminal for the logged error.

**CORS error** &mdash; only relevant if you're serving the frontend from somewhere other than the Vite dev
server's proxy. Add your frontend's origin to `CORS_ORIGINS` in `.env`.

**Frontend cannot connect to backend** &mdash; confirm the backend is running on port 8000 (`curl
http://localhost:8000/api/health` should return `{"status":"ok",...}`). The frontend dev server proxies `/api`
to `http://localhost:8000` (see `frontend/vite.config.ts`) &mdash; if you changed the backend port, update the
proxy target there too.

**PowerShell execution policy blocks `Activate.ps1`** &mdash;
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
then re-run `.\venv\Scripts\Activate.ps1`. This only changes the policy for the current terminal session.

**Virtual environment activation (Windows)** &mdash; always `.\venv\Scripts\Activate.ps1` in PowerShell (not
`source venv/bin/activate`, which is macOS/Linux). In `cmd.exe`, use `venv\Scripts\activate.bat` instead.

## 21. 🛠️ Technology Stack

### 🎨 Frontend

<p>
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white" />
  <img src="https://img.shields.io/badge/React_Router-7-CA4245?logo=reactrouter&logoColor=white" />
  <img src="https://img.shields.io/badge/Axios-HTTP_Client-5A29E4?logo=axios&logoColor=white" />
  <img src="https://img.shields.io/badge/React_Query-5-FF4154?logo=reactquery&logoColor=white" />
  <img src="https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white" />
  <img src="https://img.shields.io/badge/Recharts-3-22B5BF" />
</p>

### ⚙️ Backend & API

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Uvicorn-ASGI-499848?logo=uvicorn&logoColor=white" />
  <img src="https://img.shields.io/badge/Pydantic-2-E92063?logo=pydantic&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2-D71F00?logo=sqlalchemy&logoColor=white" />
  <img src="https://img.shields.io/badge/REST_API-Architecture-02569B" />
</p>

### 🤖 AI, OCR & Document Intelligence

<p>
  <img src="https://img.shields.io/badge/Tesseract-OCR-4285F4?logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-Computer_Vision-5C3EE8?logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-Scientific_Computing-013243?logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-Data_Processing-150458?logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/Pillow-Image_Processing-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Graphviz-Workflow_Visualization-FF6B35" />
  <img src="https://img.shields.io/badge/JiWER-OCR_Evaluation-7B1FA2" />
</p>

### 🗄️ Data & Storage

<p>
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?logo=sqlalchemy&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-Prototype-003B57?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Production_Target-4169E1?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/PostGIS-GIS_Extension-4169E1?logo=postgresql&logoColor=white" />
</p>

### 🗺️ GIS & Spatial Intelligence

<p>
  <img src="https://img.shields.io/badge/Leaflet-Interactive_Maps-199900?logo=leaflet&logoColor=white" />
  <img src="https://img.shields.io/badge/PostGIS-Spatial_Data-4169E1?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/GeoJSON-Geospatial_Data-8BC34A" />
</p>

### 🔐 Authentication & Security

<p>
  <img src="https://img.shields.io/badge/JWT-Authentication-000000?logo=jsonwebtokens&logoColor=white" />
  <img src="https://img.shields.io/badge/bcrypt-Password_Hashing-338033" />
  <img src="https://img.shields.io/badge/RBAC-Role_Based_Access-4B5563" />
  <img src="https://img.shields.io/badge/Environment_Variables-.env-6B7280" />
</p>

### 📄 Document & PDF Processing

<p>
  <img src="https://img.shields.io/badge/PyMuPDF-PDF_Processing-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/ReportLab-PDF_Generation-0A7B83?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Multipart-File_Uploads-6B7280" />
</p>

### 🧪 Testing & Code Quality

<p>
  <img src="https://img.shields.io/badge/Pytest-Testing-0A9EDC?logo=pytest&logoColor=white" />
  <img src="https://img.shields.io/badge/HTTPX-API_Testing-7B42BC" />
  <img src="https://img.shields.io/badge/OXLint-Linting-111827" />
  <img src="https://img.shields.io/badge/TypeScript-Static_Typing-3178C6?logo=typescript&logoColor=white" />
</p>

### 🐳 DevOps & Development

<p>
  <img src="https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker_Compose-Multi--Service-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Git-Version_Control-F05032?logo=git&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub-Code_Hosting-181717?logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/VS_Code-Development-007ACC?logo=visualstudiocode&logoColor=white" />
</p>

### 🧰 Core Languages

<p>
  <img src="https://img.shields.io/badge/Python-Primary-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-Frontend-3178C6?logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-Frontend_Runtime-F7DF1E?logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/SQL-Database-336791?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/HTML5-Markup-E34F26?logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-Styling-1572B6?logo=css3&logoColor=white" />
</p>


## 22. Deployment

`deployment/` contains a `Dockerfile` for the backend and one for the frontend, plus a root
`docker-compose.yml` that wires both together with a persistent volume for `storage/` and the SQLite file.
These are provided as a deployment starting point; they have not been run against a live container registry
or orchestrator as part of this build (no Docker daemon was available in the environment used to build this) &mdash;
validate `docker compose up --build` in your own environment before relying on it. For a real deployment, also
switch `DATABASE_URL` to PostgreSQL and set a strong, random `SECRET_KEY`.

## 23. Security

- Passwords hashed with bcrypt, never stored or logged in plain text
- JWT bearer auth; role is always resolved server-side from the authenticated user's account row, never
  accepted from the client
- RBAC enforced on every mutating endpoint via FastAPI dependencies (see `backend/app/middleware/auth.py`)
- File upload validation: content-type allowlist, size limit, server-generated filenames (the original
  filename is stored as metadata only, never used as a filesystem path)
- No secrets or credentials in source; everything sensitive comes from `.env` (see `.env.example`)
- Centralized exception handling: the client never sees a raw stack trace (`backend/app/main.py`)
- Every mutating action is written to an append-only audit log
- This is a **prototype's** security posture, not a certified/audited one &mdash; see Limitations.

## 24. Limitations

Being direct about where this stands, per the project's own technical-honesty requirement:

- **OCR accuracy is currently low on degraded scans.** Measured on the 3-document labelled sample set:
  macro-average field F1 = **0.042**, mean character error rate = **62%** (re-run any time via **State
  Reports &rarr; Run Evaluation**, admin only &mdash; this number is never hard-coded). The OCR engine is
  off-the-shelf Tesseract; it is not custom-trained, and it does not handle handwriting. This is exactly why
  the human verification workspace exists as a mandatory step, not an optional one.
- **GIS positions are locality-level approximations**, not surveyed cadastral parcel boundaries &mdash; there
  is no real survey dataset available to this project. The map UI labels this explicitly.
- **Sample/demo data is entirely fictional**, generated by `ai/generate_samples.py`.
- **No government system integration exists** (DILRMP, state LRMS, etc.) &mdash; the architecture is
  integration-ready (a clean adapter boundary), not integrated.
- Multi-page PDFs are split into pages and each page is processed independently as its own record; there's no
  cross-page record merging.
- No automated frontend test suite yet (backend has 20 passing tests; frontend is verified via a clean
  TypeScript build and manual/proxy integration testing during this build).
- Record verification hash is a SHA-256 integrity fingerprint, not a PKI digital signature with legal
  non-repudiation.

## 25. Future Scope

- Swap in a trained OCR/NER model as the sample set grows (the adapter boundary in `pipeline_service.py`
  exists specifically for this)
- Real DILRMP/state LRMS integration behind the same adapter pattern
- Multi-page record merging for documents that span several physical pages
- Alembic migrations for schema evolution against a production PostgreSQL database
- Frontend automated test suite (Vitest + React Testing Library)
- Continuous-learning loop: officer corrections already flow into the audit log; the next step is exporting
  them as a labelled fine-tuning/evaluation dataset (see `ai/README.md`'s own upgrade-path notes)

## Demo Walkthrough

1. Sign in as the Verification Officer (or use the quick demo card)
2. **Dashboard** &mdash; live counts across the pipeline
3. **Bulk Ingestion** &mdash; upload a PDF/JPG/PNG, click Process
4. You're dropped into the **Verification Workspace**: the real scanned image on the left, extracted fields
   on the right with real confidence scores and real source-highlight boxes; accept, edit, or reject each field
5. Once every flagged field is resolved and validation is clean, **Verify Record**
6. **Archive Registry** to search, **GIS Explorer** to see it on the map, **Export PDF** for the official report
7. **Audit Trails** to see every action logged, **State Reports** to re-run the real accuracy evaluation
