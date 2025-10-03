# Marketing Dashboard (Case)

This repository contains a small dashboard app for marketing metrics.

Structure:
- backend/ - FastAPI application using CSV files as data sources
- frontend/ - React (Vite) application using MUI for UI

## Run locally

Backend (Python 3.11+ recommended):

1. Create a virtualenv and install requirements

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

2. Run the API

```powershell
# from project root
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (Node.js 18+ recommended):

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the API at `http://localhost:8000` by default. You can change the API URL by setting `VITE_API_URL` in the frontend environment.

## Quick backend tests (local)

After installing backend requirements, you can run a small test script that exercises login and metrics endpoints:

```powershell
# from project root
python backend\test_api.py
```

This uses FastAPI's TestClient so it doesn't require the server to be running and will print simple status codes and responses to help verify the setup.

## Deployment suggestions

- Frontend: Deploy to Vercel (link the repo, build command `npm run build`, output dir `dist`). Vercel will auto-detect Vite projects.
- Backend: Use Railway/Render/Heroku to deploy the FastAPI service. Alternatively build a lightweight Docker image and deploy anywhere.

Notes about features:
- Login via `/token` (email/password) — example credentials exist in `backend/data/users.csv`.
- `/metrics` supports date filtering (`start_date`, `end_date`), sorting (`sort_by`, `sort_dir`), and pagination (`page`, `page_size`). The `cost_micros` column is omitted for non-admin users.

## Next steps
- Add tests and CI
- Improve UI design and add charts

