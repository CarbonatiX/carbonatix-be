# Review Package - Task 5

## Commits
ac8e6bd feat: add FastAPI dependencies for DB and auth

## Diff Stats
 server/deps.py | 37 +++++++++++++++++++++++++++++++++++++
 1 file changed, 37 insertions(+)

## Full Diff
diff --git a/server/deps.py b/server/deps.py
new file mode 100644
index 0000000..6656ac5
--- /dev/null
+++ b/server/deps.py
@@ -0,0 +1,37 @@
+from fastapi import Depends, HTTPException, status
+from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
+from .config import settings
+from .database import get_database
+from .auth import verify_token
+
+security = HTTPBearer()
+
+
+def get_db():
+    db = get_database()
+    if db is None:
+        raise HTTPException(
+            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
+            detail="Database not available"
+        )
+    return db
+
+
+def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
+    token = credentials.credentials
+    payload = verify_token(token)
+    if payload is None:
+        raise HTTPException(
+            status_code=status.HTTP_401_UNAUTHORIZED,
+            detail="Invalid or expired token"
+        )
+    return payload
+
+
+def require_admin(user: dict = Depends(get_current_user)):
+    if user.get("role") != "admin":
+        raise HTTPException(
+            status_code=status.HTTP_403_FORBIDDEN,
+            detail="Admin access required"
+        )
+    return user
