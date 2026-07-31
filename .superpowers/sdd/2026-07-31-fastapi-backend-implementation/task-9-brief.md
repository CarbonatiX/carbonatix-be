### Task 9: Create Main Application (`main.py`)

**Files:**
- Create: `server/main.py`

**Interfaces:**
- Consumes: All routers from Tasks 6-8
- Produces: FastAPI app instance

- [ ] **Step 1: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, items, admin

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


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

- [ ] **Step 2: Verify main.py imports correctly**

Run: `python -c "from server.main import app"`
Expected: No import errors

- [ ] **Step 3: Commit**

```bash
git add server/main.py
git commit -m "feat: create FastAPI main application with router registration"
```
