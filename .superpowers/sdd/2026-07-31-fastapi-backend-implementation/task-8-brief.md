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
