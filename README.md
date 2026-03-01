## CSIDC Industrial Land Compliance Monitoring

End-to-end geospatial system to monitor industrial plot utilisation for Chhattisgarh State Industrial Development Corporation (CSIDC) using Sentinel‑2, NDVI/NDBI, and PostGIS.

### Backend (FastAPI + PostGIS + Earth Engine)

- **Tech**: FastAPI, SQLAlchemy, GeoAlchemy2, PostGIS, Earth Engine Python API, APScheduler, ReportLab.
- **Key endpoints** (base: `http://localhost:8000/api/v1`):
  - `POST /analysis/run-analysis` – trigger T1 vs T2 Sentinel‑2 analysis for an industrial area.
  - `GET /analysis/{satellite_run_id}/report.pdf` – download PDF compliance report.
  - `GET /analysis/runs` – list recent satellite runs.
  - `GET /plots` – list plots.
  - `GET /plots/latest-analysis` – plots with latest risk metrics.
  - `GET /plots/geojson` – plot boundaries as GeoJSON for mapping.

#### Local backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # on Windows
pip install -r requirements.txt
```

Create a database and enable PostGIS, then apply schema:

```bash
createdb csidc_industrial
psql -d csidc_industrial -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -d csidc_industrial -f backend/db/schema.sql
```

Copy and edit `backend/example.env` to `.env` in `backend/` and set your database credentials and (optionally) Earth Engine service account.

Run the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI: `http://localhost:8000/docs`.

### Earth Engine integration

- Configure:
  - `GEE_SERVICE_ACCOUNT=your-sa@project.iam.gserviceaccount.com`
  - `GEE_PRIVATE_KEY_PATH=absolute/or/container/path/to/gee-key.json`
- The analysis pipeline:
  - Fetches Sentinel‑2 SR (harmonised) for AOI and dates.
  - Applies SCL-based cloud mask.
  - Computes NDVI and NDBI.
  - Derives built‑up and vegetation masks.
  - Vectorises built‑up mask and overlays with plot boundaries.
  - Detects encroachment polygons and computes per‑plot metrics and risk scores.

### Frontend (React + Leaflet + Recharts)

- **Tech**: React, Vite, TypeScript, React‑Leaflet, Recharts, Axios.
- **Features**:
  - Map view of all plots with risk‑based colouring.
  - Compliance summary (encroached, vacant, closed, risk distribution).
  - Plot table with per‑plot status.
  - Run selector (T1 vs T2) and PDF report download button.

Local dev:

```bash
cd frontend
npm install
npm run dev
```

By default the frontend expects `VITE_API_BASE_URL=http://localhost:8000/api/v1`. Configure via `.env` in `frontend/` if needed.

### Running everything locally (summary)

- Start **PostGIS** and apply `backend/db/schema.sql`.
- Run the **backend** with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.
- Run the **frontend** with `npm run dev` in `frontend/`.
- Open the dashboard at `http://localhost:5173` and the API docs at `http://localhost:8000/docs`.



