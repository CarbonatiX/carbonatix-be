# CarbonatiX Backend

FastAPI API for CarbonatiX / SmartSmelt: auth, company site-spec, digital twin metadata, document extraction, RKEF emissions & compliance, forecast stubs, and the regulatory advisor (SSE).

The product UI lives in the sibling repo **`carbonatix-fe`** (Next.js), not in this repository.

## Prerequisites

- **Python 3.12+** (CI targets 3.12; 3.13/3.14 usually work)
- **MongoDB** (local install or Docker)
- Optional: **Docker** / Docker Compose (Mongo only is enough for local API work)
- Optional: **Elice** + **Helpy** credentials for advisor SSE and document OCR

## Quick start

### 1. Clone and enter the repo

```bash
cd carbonatix-be
```

### 2. Environment

```bash
cp server/.env.example server/.env
```

Edit `server/.env`:

| Variable | Required | Purpose |
|----------|----------|---------|
| `MONGODB_URI` | Yes | Mongo connection string |
| `MONGODB_DB_NAME` | Yes | Database name |
| `JWT_SECRET_KEY` | Yes | Long random string for JWT signing |
| `ELICE_API_KEY` | No* | Advisor + document interpret |
| `ELICE_BASE_URL` | No* | Elice OpenAI-compatible base URL |
| `ELICE_MODEL` | No | Defaults to `gpt-5.6-sol` |
| `HELPY_BASE_URL` | No* | Helpy Document Vision (OCR) |

\*Without Elice/Helpy, register → emissions → commit run still works; recommendation SSE and document OCR fail cleanly.

### 3. Start MongoDB

Preferred (Compose database service only — the `frontend` Compose service is a legacy Streamlit image and is not the MVP UI):

```bash
docker compose up -d database
```

Point `MONGODB_URI` at `mongodb://localhost:27017` (or your Atlas / remote URI).

### 4. Install and run the API

From the **repo root** (`carbonatix-be`):

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

Run Uvicorn with `server` on `PYTHONPATH` (matches how tests resolve imports):

```bash
# Windows PowerShell
$env:PYTHONPATH = ".;server"
uvicorn server.main:app --reload --port 8000

# macOS/Linux
export PYTHONPATH=".:server"
uvicorn server.main:app --reload --port 8000
```

Equivalent alternative — run from the `server` package directory:

```bash
cd server
uvicorn main:app --reload --port 8000
```

### 5. Verify

| Check | URL / command |
|-------|----------------|
| Health | `GET http://localhost:8000/health` |
| OpenAPI | http://localhost:8000/docs |

On first start with an empty DB, [server/seed.py](server/seed.py) creates a demo admin (if no users exist yet):

- **Email:** `demo@carbonatix.com`
- **Password:** `test123!`

Registering a new user also seeds the five bundled twin process nodes so form-path `POST /runs` is not blocked.

## Pair with the frontend

In `carbonatix-fe`:

```bash
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

Open the Next.js app (typically http://localhost:3000).

**Demo / QA click-paths** for surplus, deficit, OCR-off, advisor-down, etc.: see [`../docs/USER_FLOWS_MVP.md`](../docs/USER_FLOWS_MVP.md).

## Tests

From `carbonatix-be` (uses mongomock; no live Mongo required):

```bash
pytest
```

## API surface (MVP)

| Area | Prefix | Notes |
|------|--------|--------|
| Auth | `POST /auth/register`, `POST /auth/login` | JWT Bearer |
| Company | `GET` / `PUT /company` | Site spec + period cap |
| Twin | `/twin/model`, `/twin/nodes`, `/twin/gaps` | Bundled nodes auto-seeded for form path |
| Documents | `POST /documents` | OCR when Helpy/Elice configured |
| Emissions | `POST /emissions` | Stateless RKEF calculator |
| Runs | `POST /runs`, `GET /runs/{id}` | Immutable snapshot; prices from Mongo forecasts when seeded |
| Forecasts | `GET /forecasts` | Seeded ML Ni + carbon series (`data/forecasts_mvp.json`); stubs only if Mongo empty |
| Advisor | `GET /runs/{id}/recommendation` | SSE; requires Elice |

Stub / fallback market figures (see `server/pricing.py`, used only when forecasts collection is empty): carbon **≈59,102 IDR/t**, nickel **16,915 USD/t**, carbon tax **30,000 IDR/t**.

### Forecast fixture

On API startup, `seed_forecasts` upserts [`data/forecasts_mvp.json`](data/forecasts_mvp.json) into Mongo when the `forecasts` collection is empty (or when `FORCE_FORECAST_SEED=1`).

Rebuild the fixture from sibling `carbonatix-ml` artifacts (needs ML `.venv` with prophet):

```bash
# from carbonatix-ml
.venv\Scripts\python.exe ..\carbonatix-be\server\scripts\build_forecasts_fixture.py
```

Sources: nickel prototype `forecasts["30"]`, carbon `artifacts/carbon_prophet_20260810.pkl` → `predict(30)`.

## Project layout

```
├── data/
│   └── forecasts_mvp.json  # Packaged GET /forecasts envelope (seeded to Mongo)
├── server/                 # FastAPI app
│   ├── main.py             # Entry + lifespan (indexes + seed)
│   ├── config.py           # Settings from server/.env
│   ├── .env.example        # Template (copy to .env)
│   ├── router.py           # HTTP routes
│   ├── seed.py             # Demo user + forecast fixture seed
│   ├── scripts/            # One-shot builders (e.g. forecasts fixture)
│   ├── emissions/          # Calculator + compliance
│   ├── advisor/            # Corpus, prompt, SSE pipeline
│   ├── ingestion/          # Document vision / mapping
│   ├── models/             # Mongo helpers
│   └── services/           # Domain services
├── test/                   # pytest
├── mdns/                   # Optional LAN mDNS helper
├── compose.yaml            # Mongo (+ legacy API/Streamlit images)
├── Dockerfile              # API image
└── requirements.txt
```

## Advisor behaviour

- Model default: **`gpt-5.6-sol`** via Elice (`ELICE_MODEL` overrides).
- Missing Elice config → synthesise/assemble fails; emission and compliance panels must still stand (FE shows “rekomendasi tidak tersedia”).
- Deficit runs include buy vs tax vs abate figures; with stub prices, **tax wins** (42k > 30k).

## Optional: API in Docker

```bash
docker compose up -d database server
```

Ensure `server/.env` matches the Compose network (for the `server` service, Mongo host is often `database` rather than `localhost`). The Compose **`frontend`** service is legacy Streamlit — use `carbonatix-fe` instead.

## Optional: `carbonatix.local` (mDNS)

For LAN demos only. Add `127.0.0.1 carbonatix.local` to your hosts file, then:

```bash
pip install zeroconf
cd mdns
HOST_IP=<your-lan-ip> python publish.py
```

## Troubleshooting

**Mongo connection refused** — confirm `docker compose ps database` (or local `mongod`) and that `MONGODB_URI` matches.

**`POST /runs` 422 with gaps** — new accounts get bundled twin nodes automatically; orphan document process types that are not on the twin still block commit.

**Advisor empty** — set `ELICE_API_KEY` and `ELICE_BASE_URL` (model-specific deployment URL). OCR also needs `HELPY_BASE_URL`.

**Port 8000 in use** — change `--port` or stop the other process (`netstat -ano | findstr :8000` on Windows).
