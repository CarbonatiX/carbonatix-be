# FastAPI Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create FastAPI backend with modular router structure for auth, items, and admin endpoints

**Architecture:** Modular FastAPI app with separate routers for each domain, dependency injection for DB and auth, JWT-based authentication

**Tech Stack:** FastAPI, uvicorn, pymongo, python-jose, bcrypt, pydantic-settings

## Global Constraints
- Reuse existing auth.py functions (hash_password, check_password, create_token, verify_token)
- Keep existing database.py connection
- JWT token in Authorization header: `Bearer <token>`
- Role-based access: admin can manage users, all authenticated users can manage items
- MongoDB collections: users, items

---

### Task 5: Create Dependencies (`deps.py`)

**Files:**
- Create: `server/deps.py`

**Interfaces:**
- Consumes: `server/config.py` (settings), `server/database.py` (get_database), `server/auth.py` (verify_token)
- Produces: `get_db()`, `get_current_user()`, `require_admin()`

- [ ] **Step 1: Create deps.py with get_db dependency**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings
from .database import get_database
from .auth import verify_token

security = HTTPBearer()


def get_db():
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    return db


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload


def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
```

- [ ] **Step 2: Verify deps.py is syntactically correct**

Run: `python -c "from server.deps import get_db, get_current_user, require_admin"`
Expected: No import errors

- [ ] **Step 3: Commit**

```bash
git add server/deps.py
git commit -m "feat: add FastAPI dependencies for DB and auth"
```

---

### Task 6: Create Auth Router (`routers/auth.py`)

**Files:**
- Create: `server/routers/__init__.py`
- Create: `server/routers/auth.py`

**Interfaces:**
- Consumes: `server/deps.py` (get_db), `server/auth.py` (login, register)
- Produces: POST `/auth/login`, POST `/auth/register`

- [ ] **Step 1: Create routers/__init__.py**

```python
```

- [ ] **Step 2: Create routers/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..deps import get_db
from ..auth import login as auth_login, register as auth_register

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    name: str
    password: str


class TokenResponse(BaseModel):
    username: str
    name: str
    role: str
    token: str


class MessageResponse(BaseModel):
    message: str


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db=Depends(get_db)):
    result = auth_login(db, req.username, req.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )
    return result


@router.post("/register", response_model=MessageResponse)
def register(req: RegisterRequest, db=Depends(get_db)):
    success, message = auth_register(db, req.username, req.name, req.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    return {"message": message}
```

- [ ] **Step 3: Verify auth router imports correctly**

Run: `python -c "from server.routers.auth import router"`
Expected: No import errors

- [ ] **Step 4: Commit**

```bash
git add server/routers/
git commit -m "feat: add auth router with login and register endpoints"
```

---

### Task 7: Create Items Router (`routers/items.py`)

**Files:**
- Create: `server/routers/items.py`

**Interfaces:**
- Consumes: `server/deps.py` (get_db, get_current_user)
- Produces: GET `/items`, POST `/items`, DELETE `/items/{name}`

- [ ] **Step 1: Create routers/items.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/items", tags=["items"])


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemResponse(BaseModel):
    name: str
    description: str
    author: str


class MessageResponse(BaseModel):
    message: str


@router.get("", response_model=list[ItemResponse])
def list_items(db=Depends(get_db)):
    items = list(db["items"].find({}, {"_id": 0}))
    return items


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_item(req: ItemCreate, user: dict = Depends(get_current_user), db=Depends(get_db)):
    db["items"].insert_one({
        "name": req.name,
        "description": req.description,
        "author": user["username"]
    })
    return {"message": "Item berhasil ditambahkan"}


@router.delete("/{name}", response_model=MessageResponse)
def delete_item(name: str, user: dict = Depends(get_current_user), db=Depends(get_db)):
    result = db["items"].delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item tidak ditemukan"
        )
    return {"message": "Item berhasil dihapus"}
```

- [ ] **Step 2: Verify items router imports correctly**

Run: `python -c "from server.routers.items import router"`
Expected: No import errors

- [ ] **Step 3: Commit**

```bash
git add server/routers/items.py
git commit -m "feat: add items router with CRUD endpoints"
```

---

### Task 8: Create Admin Router (`routers/admin.py`)

**Files:**
- Create: `server/routers/admin.py`

**Interfaces:**
- Consumes: `server/deps.py` (get_db, require_admin), `server/auth.py` (get_all_users, delete_user)
- Produces: GET `/admin/users`, DELETE `/admin/users/{username}`

- [ ] **Step 1: Create routers/admin.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..deps import get_db, require_admin
from ..auth import get_all_users as auth_get_all_users, delete_user as auth_delete_user

router = APIRouter(prefix="/admin", tags=["admin"])


class UserResponse(BaseModel):
    username: str
    name: str
    role: str


class MessageResponse(BaseModel):
    message: str


@router.get("/users", response_model=list[UserResponse])
def list_users(user: dict = Depends(require_admin), db=Depends(get_db)):
    return auth_get_all_users(db)


@router.delete("/users/{username}", response_model=MessageResponse)
def delete_user(username: str, user: dict = Depends(require_admin), db=Depends(get_db)):
    if username == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak dapat menghapus admin"
        )
    auth_delete_user(db, username)
    return {"message": f"User {username} berhasil dihapus"}
```

- [ ] **Step 2: Verify admin router imports correctly**

Run: `python -c "from server.routers.admin import router"`
Expected: No import errors

- [ ] **Step 3: Commit**

```bash
git add server/routers/admin.py
git commit -m "feat: add admin router for user management"
```

---

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

---

### Task 10: Final Testing and Cleanup

**Files:**
- Delete: `server/db.py` (duplicate)
- Modify: `server/auth.py` (remove unused functions if any)
- Modify: `requirements.txt` (add FastAPI dependencies)

**Interfaces:**
- Consumes: All previous tasks
- Produces: Clean, working codebase

- [ ] **Step 1: Remove duplicate db.py**

Run: `Remove-Item -LiteralPath "C:\Users\user\Documents\Coding\trial-streamlit\server\db.py"`
Expected: File deleted

- [ ] **Step 2: Update requirements.txt**

Add to requirements.txt:
```
fastapi
uvicorn
python-jose[cryptography]
```

- [ ] **Step 3: Verify FastAPI app starts**

Run: `cd server && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
Expected: Server starts without errors

- [ ] **Step 4: Test health endpoint**

Run: `curl http://localhost:8000/health`
Expected: `{"status":"healthy"}`

- [ ] **Step 5: Test auth endpoints**

Run: 
```bash
curl -X POST http://localhost:8000/auth/register -H "Content-Type: application/json" -d '{"username":"test","name":"Test User","password":"test123"}'
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"username":"test","password":"test123"}'
```
Expected: Register returns message, login returns token

- [ ] **Step 6: Test items endpoints with token**

Run:
```bash
TOKEN=<token_from_login>
curl -X GET http://localhost:8000/items -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8000/items -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"name":"test","description":"test item"}'
```
Expected: Items list and create work

- [ ] **Step 7: Commit cleanup**

```bash
git add -A
git commit -m "chore: cleanup duplicate files and add FastAPI dependencies"
```
