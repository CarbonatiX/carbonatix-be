# CarbonatiX ERP

Carbon emission monitoring and management platform with digital twin simulation.

## Tech Stack

- **Backend:** Python 3.14, FastAPI, Uvicorn
- **Frontend:** Streamlit
- **Database:** MongoDB
- **DevOps:** Docker, Docker Compose

## Prerequisites

- [Docker](https://www.docker.com/get-started/) with Docker Compose
- Python 3.14+ (for local development)
- [Zeroconf](https://pypi.org/project/zeroconf/) (for `carbonatix.local` domain)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/CarbonatiX/carbonatix-be.git
cd carbonatix-be
```

### 2. Create environment files

Create `.env` in the project root:

```env
HOST_IP=172.16.35.188
```

Create `server/.env`:

```env
MONGODB_URI=mongodb://<username>:<password>@<host>:27017/?ssl=true&authSource=admin
MONGODB_DB_NAME=carbonatix-db
JWT_SECRET_KEY=your-secret-key-here
```

### 3. Start with Docker Compose

```bash
docker compose up -d
```

This starts three services:

| Service | Container | URL |
|---------|-----------|-----|
| Frontend (Streamlit) | carbonatix-frontend | http://localhost |
| Backend (FastAPI) | carbonatix-api | http://localhost:8000 |
| Database (MongoDB) | carbonatix-db | localhost:27017 |

### 4. Access the application

Open **http://localhost** in your browser.

## Local Domain Setup (`carbonatix.local`)

To access the app via `http://carbonatix.local` instead of `http://localhost`:

### On your machine

Add this line to your hosts file:

- **Windows:** `C:\Windows\System32\drivers\etc\hosts`
- **Linux/macOS:** `/etc/hosts`

```
127.0.0.1 carbonatix.local
```

### On other devices (LAN)

Run the mDNS broadcaster from your development machine:

```bash
pip install zeroconf

cd mdns
HOST_IP=<your-lan-ip> python publish.py
```

Replace `<your-lan-ip>` with your machine's WiFi/LAN IP (e.g., `172.16.35.188`).

To find your LAN IP:

- **Windows:** `ipconfig` → look for IPv4 under WiFi adapter
- **Linux/macOS:** `ip addr show` or `ifconfig`

To disable: press `Ctrl+C` in the terminal running `publish.py`.

## Development

### Run without Docker

**Backend:**

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn server.main:app --reload --port 8000
```

**Frontend:**

```bash
cd client
pip install streamlit httpx
streamlit run app.py --server.port 8501
```

### Useful Docker commands

```bash
# View logs
docker compose logs -f

# Restart a specific service
docker compose restart server

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build

# View running containers
docker compose ps
```

## Project Structure

```
carbonatix-be/
├── server/                 # FastAPI backend
│   ├── main.py            # App entry point
│   ├── config.py          # Environment settings
│   ├── database.py        # MongoDB connection
│   ├── auth.py            # Authentication
│   ├── router.py          # API routes
│   ├── schemas.py         # Pydantic schemas
│   ├── models/            # Data models
│   └── services/          # Business logic
├── client/                # Streamlit frontend
│   ├── app.py             # Main app
│   ├── api.py             # API client
│   └── pages/             # Page components
├── mdns/                  # mDNS broadcaster
│   └── publish.py         # Broadcasts carbonatix.local on LAN
├── compose.yaml           # Docker Compose config
├── Dockerfile             # Backend container
├── Dockerfile.streamlit   # Frontend container
└── requirements.txt       # Python dependencies
```

## API Endpoints

| Module | Prefix | Description |
|--------|--------|-------------|
| Auth | `/auth` | Login, Register, Approval |
| Company | `/company` | Company profile |
| Twin Model | `/twin` | Node models and 3D simulation |
| Documents | `/documents` | Document upload & extraction |
| Emissions | `/emissions` | Emission monitoring |
| Runs | `/runs` | Calculation runs |
| Forecasts | `/forecasts` | Emission forecasts |
| Recommendations | `/runs/{run_id}/recommendation` | Recommendations |

## Troubleshooting

**Port already in use:**

```bash
# Find process using the port
# Windows:
netstat -ano | findstr :80
# Linux/macOS:
lsof -i :80

# Kill the process or change the port in compose.yaml
```

**Container won't start:**

```bash
docker compose logs <service-name>
```

**MongoDB connection refused:**

Ensure `server/.env` has the correct `MONGODB_URI` and the database container is running:

```bash
docker compose ps database
```

**`carbonatix.local` not resolving:**

- Verify hosts file entry exists and is correct
- Flush DNS cache: `ipconfig /flushdns` (Windows) or `sudo systemd-resolve --flush-caches` (Linux)
