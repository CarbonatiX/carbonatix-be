# FastAPI Conversion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the Streamlit application to a FastAPI REST API backend

**Architecture:** Modular FastAPI with separate routers for auth, items, and admin endpoints. Uses pydantic-settings for configuration and MongoDB Atlas for data storage.

**Tech Stack:** FastAPI, uvicorn, pymongo, bcrypt, PyJWT, pydantic-settings

## Global Constraints

- MongoDB Atlas connection string from environment variables
- JWT token expiration: 24 hours
- Password hashing: bcrypt
- API prefix: `/api`
- Keep existing `client/` directory for reference

---

### Task 1: Update Requirements and Configuration

**Files:**
- Modify: `requirements.txt`
- Create: `.env.example`
- Create: `server/config.py`

**Interfaces:**
- Consumes: None
- Produces: `Settings` class with `MONGODB_URI`, `MONGODB_DB_NAME`, `JWT_SECRET_KEY`

- [ ] **Step 1: Update requirements.txt**

```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pymongo>=4.6.0
bcrypt>=4.1.0
PyJWT>=2.8.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
```

- [ ] **Step 2: Create .env.example**

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=carbonatix
JWT_SECRET_KEY=your-secret-key-here
```

- [ ] **Step 3: Create server/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DB_NAME: str
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

- [ ] **Step 4: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: Success

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .env.example server/config.py
git commit -m "feat: add FastAPI dependencies and configuration"
```

---

### Task 2: Update Database Connection

**Files:**
- Modify: `server/db.py` → rename to `server/database.py`

**Interfaces:**
- Consumes: `settings.MONGODB_URI`, `settings.MONGODB_DB_NAME`
- Produces: `get_database()` function returning MongoDB database

- [ ] **Step 1: Create server/database.py**

```python
import pymongo
from pymongo.errors import ConnectionFailure
from config import settings


_client = None


def get_database():
    global _client
    if _client is None:
        try:
            _client = pymongo.MongoClient(settings.MONGODB_URI)
            _client.admin.command("ping")
        except ConnectionFailure:
            return None
    return _client[settings.MONGODB_DB_NAME]
```

- [ ] **Step 2: Test database connection**

Run: `python -c "from server.database import get_database; db = get_database(); print('Connected' if db else 'Failed')"`
Expected: Connected

- [ ] **Step 3: Commit**

```bash
git add server/database.py
git commit -m "feat: update database connection for FastAPI"
```

---

### Task 3: Update Authentication Module

**Files:**
- Modify: `server/auth.py`

**Interfaces:**
- Consumes: `settings.JWT_SECRET_KEY`
- Produces: `hash_password()`, `check_password()`, `create_token()`, `verify_token()`, `login()`, `register()`, `get_all_users()`, `delete_user()`

- [ ] **Step 1: Update server/auth.py**

```python
import bcrypt
import jwt
import datetime
from config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(username: str, role: str) -> str:
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login(db, username: str, password: str) -> dict | None:
    users = db["users"]
    user = users.find_one({"username": username})
    if user and check_password(password, user["password"]):
        token = create_token(user["username"], user.get("role", "viewer"))
        return {
            "username": user["username"],
            "name": user["name"],
            "role": user.get("role", "viewer"),
            "token": token,
        }
    return None


def register(db, username: str, name: str, password: str, role: str = "viewer") -> tuple[bool, str]:
    users = db["users"]
    if users.find_one({"username": username}):
        return False, "Username sudah ada!"

    users.insert_one({
        "username": username,
        "name": name,
        "password": hash_password(password),
        "role": role,
    })
    return True, "Register berhasil!"


def get_all_users(db) -> list:
    users = db["users"]
    return list(users.find({}, {"_id": 0, "password": 0}))


def delete_user(db, username: str) -> bool:
    users = db["users"]
    users.delete_one({"username": username})
    return True
```

- [ ] **Step 2: Test auth functions**

Run: `python -c "from server.auth import hash_password, check_password; h = hash_password('test'); print('OK' if check_password('test', h) else 'FAIL')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add server/auth.py
git commit -m "feat: update auth module to use pydantic-settings"
```

---

### Task 4: Create Pydantic Models

**Files:**
- Create: `server/models/__init__.py`
- Create: `server/models/user.py`
- Create: `server/models/item.py`

**Interfaces:**
- Consumes: None
- Produces: `UserLogin`, `UserRegister`, `UserResponse`, `ItemCreate`, `ItemResponse`

- [ ] **Step 1: Create server/models/__init__.py**

```python
from .user import UserLogin, UserRegister, UserResponse
from .item import ItemCreate, ItemResponse
```

- [ ] **Step 2: Create server/models/user.py**

```python
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    name: str
    password: str


class UserResponse(BaseModel):
    username: str
    name: str
    role: str
```

- [ ] **Step 3: Create server/models/item.py**

```python
from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemResponse(BaseModel):
    name: str
    description: str
    author: str
```

- [ ] **Step 4: Test models**

Run: `python -c "from server.models import UserLogin, ItemCreate; print('OK')"`
Expected: OK

- [ ] **Step 5: Commit**

```bash
git add server/models/
git commit -m "feat: add Pydantic models for request/response"
```

---

### Task 5: Create Dependencies

**Files:**
- Create: `server/dependencies.py`

**Interfaces:**
- Consumes: `get_database()`, `verify_token()`
- Produces: `get_db()`, `get_current_user()`, `require_admin()`

- [ ] **Step 1: Create server/dependencies.py**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_database
from auth import verify_token

security = HTTPBearer()


def get_db():
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
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

- [ ] **Step 2: Test dependencies import**

Run: `python -c "from server.dependencies import get_db, get_current_user, require_admin; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add server/dependencies.py
git commit -m "feat: add FastAPI dependencies for auth and database"
```

---

### Task 6: Create Auth Router

**Files:**
- Create: `server/routers/__init__.py`
- Create: `server/routers/auth.py`

**Interfaces:**
- Consumes: `login()`, `register()`, `get_db()`, `UserLogin`, `UserRegister`
- Produces: `POST /api/auth/login`, `POST /api/auth/register`

- [ ] **Step 1: Create server/routers/__init__.py**

```python
from .auth import router as auth_router
from .items import router as items_router
from .admin import router as admin_router
```

- [ ] **Step 2: Create server/routers/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_database
from auth import login, register
from models import UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login_endpoint(user: UserLogin):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    result = login(db, user.username, user.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )
    return result


@router.post("/register")
def register_endpoint(user: UserRegister):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    success, message = register(db, user.username, user.name, user.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    return {"message": message}
```

- [ ] **Step 3: Test auth router import**

Run: `python -c "from server.routers.auth import router; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
git add server/routers/
git commit -m "feat: add auth router with login and register endpoints"
```

---

### Task 7: Create Items Router

**Files:**
- Create: `server/routers/items.py`

**Interfaces:**
- Consumes: `get_db()`, `get_current_user()`, `ItemCreate`, `ItemResponse`
- Produces: `GET /api/items`, `POST /api/items`, `DELETE /api/items/{name}`

- [ ] **Step 1: Create server/routers/items.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_database
from dependencies import get_current_user
from models import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemResponse])
def get_items(user: dict = Depends(get_current_user)):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    items = list(db["items"].find({}, {"_id": 0}))
    return items


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, user: dict = Depends(get_current_user)):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    db["items"].insert_one({
        "name": item.name,
        "description": item.description,
        "author": user["username"]
    })
    return {"message": "Item created successfully"}


@router.delete("/{name}")
def delete_item(name: str, user: dict = Depends(get_current_user)):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    result = db["items"].delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return {"message": "Item deleted successfully"}
```

- [ ] **Step 2: Test items router import**

Run: `python -c "from server.routers.items import router; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add server/routers/items.py
git commit -m "feat: add items router with CRUD endpoints"
```

---

### Task 8: Create Admin Router

**Files:**
- Create: `server/routers/admin.py`

**Interfaces:**
- Consumes: `get_db()`, `require_admin()`, `get_all_users()`, `delete_user()`, `UserResponse`
- Produces: `GET /api/admin/users`, `DELETE /api/admin/users/{username}`

- [ ] **Step 1: Create server/routers/admin.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_database
from dependencies import require_admin
from auth import get_all_users, delete_user
from models import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
def get_users(user: dict = Depends(require_admin)):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    users = get_all_users(db)
    return users


@router.delete("/users/{username}")
def delete_user_endpoint(username: str, user: dict = Depends(require_admin)):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    if username == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )
    delete_user(db, username)
    return {"message": "User deleted successfully"}
```

- [ ] **Step 2: Test admin router import**

Run: `python -c "from server.routers.admin import router; print('OK')"`
Expected: OK

- [ ] **Step 3: Commit**

```bash
git add server/routers/admin.py
git commit -m "feat: add admin router for user management"
```

---

### Task 9: Create Main Application

**Files:**
- Create: `server/main.py`
- Modify: `server/__init__.py`

**Interfaces:**
- Consumes: `auth_router`, `items_router`, `admin_router`
- Produces: FastAPI application with all routes

- [ ] **Step 1: Create server/main.py**

```python
from fastapi import FastAPI
from routers import auth_router, items_router, admin_router

app = FastAPI(
    title="Internal App API",
    description="REST API for Internal App",
    version="1.0.0"
)

app.include_router(auth_router, prefix="/api")
app.include_router(items_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
```

- [ ] **Step 2: Update server/__init__.py**

```python
from .main import app
```

- [ ] **Step 3: Test application starts**

Run: `cd server && python -m uvicorn main:app --host 0.0.0.0 --port 8000`
Expected: Application starts without errors

- [ ] **Step 4: Test health endpoint**

Run: `curl http://localhost:8000/api/health`
Expected: `{"status":"healthy"}`

- [ ] **Step 5: Commit**

```bash
git add server/main.py server/__init__.py
git commit -m "feat: create main FastAPI application with all routers"
```

---

### Task 10: Final Testing and Cleanup

**Files:**
- Verify: All files in `server/`

**Interfaces:**
- Consumes: All previous tasks
- Produces: Working API with all endpoints

- [ ] **Step 1: Test login endpoint**

Run: `curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'`
Expected: Token response

- [ ] **Step 2: Test register endpoint**

Run: `curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"username":"testuser","name":"Test User","password":"test123"}'`
Expected: `{"message":"Register berhasil!"}`

- [ ] **Step 3: Test items endpoint (with token)**

Run: `curl -X GET http://localhost:8000/api/items -H "Authorization: Bearer <token>"`
Expected: Items list

- [ ] **Step 4: Test admin endpoint (with admin token)**

Run: `curl -X GET http://localhost:8000/api/admin/users -H "Authorization: Bearer <admin_token>"`
Expected: Users list

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete FastAPI conversion"
```

- [ ] **Step 6: Update .gitignore**

```gitignore
# Environment
.env
.venv/
venv/

# Python
__pycache__/
*.py[cod]
*$py.class

# IDE
.vscode/
.idea/

# FastAPI
server/__pycache__/
```

- [ ] **Step 7: Final commit**

```bash
git add .gitignore
git commit -m "chore: update .gitignore for FastAPI project"
```
