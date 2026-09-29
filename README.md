# SAMANVAY-WX · SIH 2026 · PS SIH26081

Hybrid AI–NWP Multi-Model Forecast Blending System
Ministry of Earth Sciences (MoES) · NCMRWF · Software Category · Disaster Management Theme

## Folder structure

```
samanvay-wx/
├── SAMANVAY-WX.html          ← Main website (open this in browser)
├── backend/
│   ├── main.py                ← FastAPI backend
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml     ← Optional: full stack (Postgres/Redis/MinIO)
└── README.md
```

## Quick start (frontend only, no backend needed)

Just open `SAMANVAY-WX.html` in Chrome, Edge, or Firefox. It works fully offline
(the deterministic mock field generator kicks in automatically) except for map
tiles and the Google Fonts / Chart.js / Leaflet CDN scripts, which need internet.

## Backend (optional, for live data)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open the HTML, go to **Backend API** in the sidebar — the status dot turns green.

## Full stack (Docker)

```bash
cd backend
docker compose up --build
```

## Features

- 7 command-centre screens: Operations Map, Model Comparison, Trust Map, Verification Lab, Extreme Guidance, Review Queue, Trust Ledger
- 10-slide auto-generated pitch deck (keyboard ← → navigation)
- Live FastAPI backend probe with graceful offline fallback
- Dark / light glass theme with persisted preference
- Real interactive maps (Leaflet + CARTO tiles)
- 8 REST endpoints: `/health`, `/models`, `/blend`, `/weights`, `/ledger`, `/trustguard`, `/verification`, `/docs`

## Deploy

- Frontend: drop `SAMANVAY-WX.html` on Netlify / Vercel / GitHub Pages.
- Backend: Railway / Render / Fly.io — `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

## Team

SIH 2026 · Problem Statement SIH26081 · MoES / NCMRWF
