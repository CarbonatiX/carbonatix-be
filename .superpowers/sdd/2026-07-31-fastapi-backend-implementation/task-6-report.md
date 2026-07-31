### Task 6: Create Auth Router (routers/auth.py)

**Status:** DONE

**What I implemented:**
- Created `server/routers/__init__.py` (empty)
- Created `server/routers/auth.py` with:
  - `LoginRequest`, `RegisterRequest`, `TokenResponse`, `MessageResponse` Pydantic models
  - `POST /auth/login` endpoint that calls `auth_login()` and returns token or 401
  - `POST /auth/register` endpoint that calls `auth_register()` and returns message or 400

**What I tested:**
- Import verification: `python -c "from server.routers.auth import router"` passed with no errors
- Files match exact specification from task brief

**Files changed:**
- `server/routers/__init__.py` (created)
- `server/routers/auth.py` (created)

**Self-review findings:**
- Implementation exactly matches task specification
- Follows existing patterns in `server/auth.py` and `server/deps.py`
- No overbuilding or missing requirements

**Commits:**
- `4081470` - feat: add auth router with login and register endpoints

**Report file:** `.superpowers/sdd/2026-07-31-fastapi-backend-implementation/task-6-report.md`