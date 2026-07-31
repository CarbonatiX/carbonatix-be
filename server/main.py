from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, items, admin, users, nodes, documents

app = FastAPI(
    title="Internal App API",
    description="API for internal application with auth, items, and admin management",
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


@app.get("/health")
def health_check():
    return {"status": "healthy"}
