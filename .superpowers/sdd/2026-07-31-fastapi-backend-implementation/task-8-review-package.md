# Review Package - Task 8

## Commits
625e955 - feat: add admin router for user management

## Diff Stats
 server/routers/admin.py | 32 ++++++++++++++++++++++++++++++++
 1 file changed, 32 insertions(+)

## Full Diff
diff --git a/server/routers/admin.py b/server/routers/admin.py
new file mode 100644
index 0000000..08be624
--- /dev/null
+++ b/server/routers/admin.py
@@ -0,0 +1,32 @@
+from fastapi import APIRouter, Depends, HTTPException, status
+from pydantic import BaseModel
+from ..deps import get_db, require_admin
+from ..auth import get_all_users as auth_get_all_users, delete_user as auth_delete_user
+
+router = APIRouter(prefix="/admin", tags=["admin"])
+
+
+class UserResponse(BaseModel):
+    username: str
+    name: str
+    role: str
+
+
+class MessageResponse(BaseModel):
+    message: str
+
+
+@router.get("/users", response_model=list[UserResponse])
+def list_users(user: dict = Depends(require_admin), db=Depends(get_db)):
+    return auth_get_all_users(db)
+
+
+@router.delete("/users/{username}", response_model=MessageResponse)
+def delete_user(username: str, user: dict = Depends(require_admin), db=Depends(get_db)):
+    if username == "admin":
+        raise HTTPException(
+            status_code=status.HTTP_400_BAD_REQUEST,
+            detail="Tidak dapat menghapus admin"
+        )
+    auth_delete_user(db, username)
+    return {"message": f"User {username} berhasil dihapus"}
