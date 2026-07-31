# FastAPI Backend Design

## Overview
Refactoring Streamlit + MongoDB app to use FastAPI backend with modular router structure.

## Scope
- Minimal CRUD: items + auth
- JWT authentication
- Role-based access (admin, viewer)
- MongoDB backend

## File Structure
```
server/
├── deps.py          # FastAPI dependencies
├── main.py          # FastAPI app entry point
├── config.py        # Settings (existing)
├── database.py      # MongoDB connection (existing)
├── auth.py          # Auth functions (existing)
├── models/
│   ├── user.py      # Pydantic models (existing)
│   └── item.py      # Pydantic models (existing)
└── routers/
    ├── auth.py      # Auth endpoints
    ├── items.py     # Items CRUD
    └── admin.py     # Admin endpoints
```

## Tasks

### Task 5: Create Dependencies (`deps.py`)
```python
# Dependencies for FastAPI
- get_db(): MongoDB database dependency
- get_current_user(): JWT token verification
- require_admin(): Admin role check dependency
```

### Task 6: Create Auth Router (`routers/auth.py`)
```python
# Endpoints
POST /auth/login → Returns JWT token
POST /auth/register → Creates new user
```

### Task 7: Create Items Router (`routers/items.py`)
```python
# Endpoints (requires auth)
GET /items → List all items
POST /items → Create item
DELETE /items/{name} → Delete item
```

### Task 8: Create Admin Router (`routers/admin.py`)
```python
# Endpoints (requires admin role)
GET /admin/users → List all users
DELETE /admin/users/{username} → Delete user
```

### Task 9: Create Main Application (`main.py`)
```python
# FastAPI app setup
- Create FastAPI instance
- Register all routers
- CORS middleware
- Health check endpoint
```

### Task 10: Final Testing and Cleanup
```python
# Tasks
- Remove duplicate db.py
- Update imports in auth.py
- Verify all endpoints work
- Update requirements.txt if needed
```

## API Endpoints Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/login | No | Login, get token |
| POST | /auth/register | No | Register new user |
| GET | /items | Yes | List items |
| POST | /items | Yes | Create item |
| DELETE | /items/{name} | Yes | Delete item |
| GET | /admin/users | Admin | List users |
| DELETE | /admin/users/{username} | Admin | Delete user |

## Dependencies
- FastAPI
- uvicorn
- python-jose (JWT)
- pymongo (existing)
- bcrypt (existing)
- pydantic-settings (existing)

## Notes
- Reuse existing auth.py functions
- Keep existing database.py connection
- JWT token in Authorization header: `Bearer <token>`
- Role-based access: admin can manage users, all authenticated users can manage items
