# CarbonatiX ERP — Tech Stack

## Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.14+ | Core language |
| **FastAPI** | ≥0.109.0 | REST API framework |
| **Uvicorn** | ≥0.27.0 | ASGI server |
| **PyMongo** | ≥4.6.0 | MongoDB driver |
| **Pydantic** | ≥2.5.0 | Data validation & schemas |
| **Pydantic Settings** | ≥2.1.0 | Environment config management |
| **PyJWT** | ≥2.8.0 | JWT token generation/verification |
| **python-jose** | ≥3.3.0 | JWT cryptography support |
| **Bcrypt** | ≥4.1.0 | Password hashing |
| **python-multipart** | ≥0.0.9 | File upload support |
| **httpx** | ≥0.27.0 | HTTP client (Streamlit → FastAPI) |
| **python-dotenv** | ≥1.0.0 | .env file loading |

## Frontend

| Technology | Purpose |
|------------|---------|
| **Streamlit** | Web UI framework |
| **httpx** | API client for backend communication |

## Database

| Technology | Purpose |
|------------|---------|
| **MongoDB** | Primary database (NoSQL) |

## DevOps

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |

## Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐     TCP      ┌─────────────────┐
│   Streamlit     │ ───────────► │    FastAPI       │ ───────────► │    MongoDB      │
│   (Client)      │              │    (Server)      │              │   (Database)    │
│   Port: 8501    │              │   Port: 8000     │              │   Port: 27017   │
└─────────────────┘              └─────────────────┘              └─────────────────┘
```

## API Endpoints

| Module | Prefix | Description |
|--------|--------|-------------|
| Auth | `/auth` | Login, Register, Approval |
| Users | `/api/v1/users` | User management |
| Nodes | `/api/v1/nodes` | RKEF process monitoring |
| Documents | `/api/v1/documents` | Document upload & extraction |
| Scans | `/api/v1/scans` | 3D scan management |
| Models | `/api/v1/models` | AI simulation |

## Project Structure

```
carbonatix-be/
├── server/
│   ├── main.py           # FastAPI app entry
│   ├── config.py         # Environment settings
│   ├── database.py       # MongoDB connection
│   ├── auth.py           # Authentication logic
│   ├── seed.py           # Seed data
│   ├── deps.py           # Dependencies
│   ├── models/           # Pydantic schemas
│   └── routers/          # API endpoints
├── client/
│   ├── app.py            # Streamlit main
│   ├── api.py            # HTTP client
│   └── pages/            # Streamlit pages
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container build
├── compose.yaml          # Docker Compose
└── .env                  # Environment variables
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DB_NAME` | Database name |
| `JWT_SECRET_KEY` | JWT signing secret |
