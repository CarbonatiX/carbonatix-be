# CarbonatiX Backend

FastAPI API for CarbonatiX / SmartSmelt: auth, company site-spec, digital twin metadata, document extraction, RKEF emissions & compliance, forecast stubs, and the regulatory advisor (SSE).

The product UI lives in the sibling repo **`carbonatix-fe`** (Next.js), not in this repository.

## Prerequisites

- **Docker** / Docker Compose — the only requirement for the quick start below; it brings its own Mongo
- **Python 3.12+** — only for the hot-reload dev loop (CI targets 3.12; 3.13/3.14 usually work)
- Optional: **Elice** + **Helpy** credentials for advisor SSE and document OCR

## Quick start

### 1. Environment

```bash
cp server/.env.example server/.env
```

Edit `server/.env`:

| Variable | Required | Purpose |
|----------|----------|---------|
| `MONGODB_URI` | Yes | Mongo connection string (Compose overrides this for the API container — see step 2) |
| `MONGODB_DB_NAME` | Yes | Database name |
| `JWT_SECRET_KEY` | Yes | Long random string for JWT signing |
| `ELICE_API_KEY` | No* | Advisor + document interpret |
| `ELICE_BASE_URL` | No* | Elice OpenAI-compatible base URL |
| `ELICE_MODEL` | No | Defaults to `gpt-5.6-sol` |
| `HELPY_BASE_URL` | No* | Helpy Document Vision (OCR) |

\*Without Elice/Helpy, register → emissions → commit run still works; recommendation SSE and document OCR fail cleanly.

### 2. Run it

```bash
docker compose up -d
```

That's the whole setup — Mongo **and** the API, with the API waiting on Mongo's healthcheck before it starts. Note there is no service name on that command: `docker compose up -d database` would start Mongo *only*, leaving nothing on port 8000.

**Which database the container uses.** `server/.env` is loaded into the container, but its `MONGODB_URI` is typically `localhost`, which inside a container means the container itself. So Compose supplies the container's own value:

| Repo-root `.env` | Container connects to |
|---|---|
| absent (default) | the bundled `database` service — self-contained, seeds `demo@carbonatix.com` on first run |
| `MONGODB_URI=<remote>` | that remote (e.g. Atlas), so you see shared team data |

Create a repo-root `.env` with a single `MONGODB_URI=...` line to aim the container at a remote. It is gitignored and read by Compose for interpolation only. An exported `MONGODB_URI` in your shell works the same way.

This repo serves the API only — the MVP UI is the sibling `carbonatix-fe` repo.

### 3. Verify

| Check | URL / command |
|-------|----------------|
| Health | `GET http://localhost:8000/health` |
| OpenAPI | http://localhost:8000/docs |

On first start with an empty DB, [server/seed.py](server/seed.py) creates a demo admin (if no users exist yet):

- **Email:** `demo@carbonatix.com`
- **Password:** `test123!`

Registering a new user also seeds the five bundled twin process nodes so form-path `POST /runs` is not blocked.

## Develop locally (hot reload)

Run the API natively against the Compose Mongo, so edits reload without a rebuild.

> This path starts **Mongo only** in Docker — note the `database` argument. The API does *not* run in a container here; you start it yourself with `uvicorn`. If you stop after the `docker compose` line, port 8000 will be empty and the frontend will fail with `ERR_CONNECTION_REFUSED`.

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d database   # Mongo ONLY — no API
uvicorn server.main:app --reload --port 8000   # the API itself
```

Run everything from the **repo root** — `server` is a normal package, so no `PYTHONPATH` is needed. This path uses `MONGODB_URI` from `server/.env` as-is (`mongodb://localhost:27017` for the Compose Mongo, or your Atlas URI).

Tests use mongomock and need no live Mongo:

```bash
pytest        # 55 tests
ruff check .
```

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
├── compose.yaml            # Mongo + API
├── Dockerfile              # API image
└── requirements.txt
```

Modules import each other by full package path (`from server.services import ...`), so the app resolves from the repo root with no `PYTHONPATH` or `sys.path` setup — in Docker, under Uvicorn, and under pytest alike.

## Advisor behaviour

- Model default: **`gpt-5.6-sol`** via Elice (`ELICE_MODEL` overrides).
- Missing Elice config → synthesise/assemble fails; emission and compliance panels must still stand (FE shows “rekomendasi tidak tersedia”).
- Deficit runs include buy vs tax vs abate figures; with stub prices, **tax wins** (42k > 30k).

## Optional: `carbonatix.local` (mDNS)

For LAN demos only. Add `127.0.0.1 carbonatix.local` to your hosts file, then:

```bash
pip install zeroconf
cd mdns
HOST_IP=<your-lan-ip> python publish.py
```

## Troubleshooting

**Mongo connection refused** — confirm `docker compose ps database` shows `healthy`, and that `MONGODB_URI` matches (`localhost` when running the API natively, `database` inside Compose).

**API starts but the DB is empty** — `get_database()` returns `None` on connection failure and startup silently skips indexing and seeding. Check `docker compose logs server` for `Seeded admin:` / `Seeded forecasts from`; if absent, Mongo was unreachable at startup.

**`POST /runs` 422 with gaps** — new accounts get bundled twin nodes automatically; orphan document process types that are not on the twin still block commit.

**Advisor empty** — set `ELICE_API_KEY` and `ELICE_BASE_URL` (model-specific deployment URL). OCR also needs `HELPY_BASE_URL`.

**Port 8000 in use** — change `--port` or stop the other process (`netstat -ano | findstr :8000` on Windows).
