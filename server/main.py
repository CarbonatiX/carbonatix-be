from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, items, admin, users, nodes, documents, scans, models
from .database import get_database
from .seed import seed_database

app = FastAPI(
    title="CarbonatiX ERP API",
    description="ERP system for nickel processing facility management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(nodes.router)
app.include_router(documents.router)
app.include_router(scans.router)
app.include_router(models.router)


@app.on_event("startup")
def startup_event():
    db = get_database()
    if db:
        seed_database(db)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
