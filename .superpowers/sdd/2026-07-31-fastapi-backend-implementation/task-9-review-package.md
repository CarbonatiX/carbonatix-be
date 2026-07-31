# Review Package - Task 9

## Commits
c385c94 — feat: create FastAPI main application with router registration

## Diff Stats
 server/main.py | 26 ++++++++++++++++++++++++++
 1 file changed, 26 insertions(+)

## Full Diff
diff --git a/server/main.py b/server/main.py
new file mode 100644
index 0000000..4d25220
--- /dev/null
+++ b/server/main.py
@@ -0,0 +1,26 @@
+from fastapi import FastAPI
+from fastapi.middleware.cors import CORSMiddleware
+from .routers import auth, items, admin
+
+app = FastAPI(
+    title="Internal App API",
+    description="API for internal application with auth, items, and admin management",
+    version="1.0.0"
+)
+
+app.add_middleware(
+    CORSMiddleware,
+    allow_origins=["*"],
+    allow_credentials=True,
+    allow_methods=["*"],
+    allow_headers=["*"],
+)
+
+app.include_router(auth.router)
+app.include_router(items.router)
+app.include_router(admin.router)
+
+
+@app.get("/health")
+def health_check():
+    return {"status": "healthy"}
