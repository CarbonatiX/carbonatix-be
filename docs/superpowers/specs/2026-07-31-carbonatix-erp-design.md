# CarbonatiX ERP — Refactor Design

## Overview

Refactor existing FastAPI backend (`server/`) to match the API schema in `api_schema_with_fastapi.md`, and refactor Streamlit client (`client/`) to call FastAPI endpoints instead of connecting directly to MongoDB.

## Scope

All 5 sections from the API schema:
1. **Users** — `/api/v1/users` (register, update, approval, list/filter)
2. **Node Data** — `/api/v1/nodes` (CRUD, parameters, time-series queries)
3. **Document Upload & Extraction** — `/api/v1/documents` (upload, extract, extracted-data, list)
4. **3D Scan** — `/api/v1/scans` (upload, list, download, delete)
5. **Models** — `/api/v1/models` (list, simulate)

## Architecture

### Backend (server/)

```
server/
├── main.py              # FastAPI app, CORS, router registration
├── config.py            # Settings (existing, unchanged)
├── database.py          # MongoDB connection (existing, unchanged)
├── deps.py              # Dependencies (get_db, get_current_user)
├── auth.py              # Auth logic (existing, add role-based auth)
├── models/              # Pydantic schemas
│   ├── __init__.py
│   ├── user.py          # User schemas (existing, extend)
│   ├── node.py          # Node + NodeParameter schemas
│   ├── document.py      # Document + Extraction schemas
│   ├── scan.py          # Scan schemas
│   └── model.py         # Model + Simulation schemas
├── routers/             # API routers
│   ├── __init__.py
│   ├── auth.py          # Auth routes (existing, keep)
│   ├── users.py         # User management routes (NEW)
│   ├── nodes.py         # Node CRUD + parameters (NEW)
│   ├── documents.py     # Document upload + extraction (NEW)
│   ├── scans.py         # 3D scan management (NEW)
│   └── models.py        # AI simulation (NEW)
```

### Client (client/)

```
client/
├── app.py               # Main Streamlit app (refactor to use API)
├── api.py               # HTTP client wrapper for FastAPI (NEW)
├── pages/
│   ├── 1_nodes.py       # Node monitoring page
│   ├── 2_documents.py   # Document management page
│   ├── 3_scans.py       # 3D scan viewer page
│   └── 4_models.py      # AI simulation page
```

## API Endpoints Summary

### Users (`/api/v1/users`)
- `POST /users` — Register user
- `PUT /users/{id}` — Update user
- `PUT /users/{id}/approve` — Approval (superadmin)
- `GET /users` — List/filter users

### Nodes (`/api/v1/nodes`)
- `POST /nodes` — Create node
- `PUT /nodes/{id}` — Update node
- `POST /nodes/{id}/parameters` — Input parameters
- `GET /nodes` — List/filter nodes
- `GET /nodes/{id}/parameters` — Get parameters (time-range query)

### Documents (`/api/v1/documents`)
- `POST /documents` — Upload document
- `POST /documents/{id}/extract` — Run extraction
- `GET /documents/{id}/extracted-data` — Get extracted data
- `GET /documents` — List/filter documents

### Scans (`/api/v1/scans`)
- `POST /scans` — Upload scan (.glb/.obj/.ply)
- `GET /scans` — List/filter scans
- `GET /scans/{id}/file` — Download scan file
- `DELETE /scans/{id}` — Delete scan

### Models (`/api/v1/models`)
- `GET /models` — List models
- `POST /models/simulate` — AI What-If simulation

## Key Decisions

1. **Versioned API**: All routes under `/api/v1/` prefix
2. **Pydantic models**: Strict validation matching the schema exactly
3. **MongoDB collections**: `users`, `nodes`, `node_parameters`, `documents`, `extracted_data`, `scans`, `models`
4. **File storage**: Scans and documents stored in `uploads/` directory
5. **Auth**: JWT token in header, role-based access (admin, superadmin, operator, viewer)
6. **Client refactoring**: Streamlit app calls FastAPI via `requests`/`httpx`, stores JWT token in session state

## Dependencies to Add

- `httpx` — Async HTTP client for Streamlit → FastAPI communication
- `python-multipart` — File upload support for FastAPI
