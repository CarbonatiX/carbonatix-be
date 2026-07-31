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
