# Review Package - Task 7

## Commits
96f2b18 — feat: add items router with CRUD endpoints

## Diff Stats
 server/routers/items.py | 47 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 47 insertions(+)

## Full Diff
diff --git a/server/routers/items.py b/server/routers/items.py
new file mode 100644
index 0000000..fb86c2b
--- /dev/null
+++ b/server/routers/items.py
@@ -0,0 +1,47 @@
+from fastapi import APIRouter, Depends, HTTPException, status
+from pydantic import BaseModel
+from ..deps import get_db, get_current_user
+
+router = APIRouter(prefix="/items", tags=["items"])
+
+
+class ItemCreate(BaseModel):
+    name: str
+    description: str
+
+
+class ItemResponse(BaseModel):
+    name: str
+    description: str
+    author: str
+
+
+class MessageResponse(BaseModel):
+    message: str
+
+
+@router.get("", response_model=list[ItemResponse])
+def list_items(db=Depends(get_db)):
+    items = list(db["items"].find({}, {"_id": 0}))
+    return items
+
+
+@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
+def create_item(req: ItemCreate, user: dict = Depends(get_current_user), db=Depends(get_db)):
+    db["items"].insert_one({
+        "name": req.name,
+        "description": req.description,
+        "author": user["username"]
+    })
+    return {"message": "Item berhasil ditambahkan"}
+
+
+@router.delete("/{name}", response_model=MessageResponse)
+def delete_item(name: str, user: dict = Depends(get_current_user), db=Depends(get_db)):
+    result = db["items"].delete_one({"name": name})
+    if result.deleted_count == 0:
+        raise HTTPException(
+            status_code=status.HTTP_404_NOT_FOUND,
+            detail="Item tidak ditemukan"
+        )
+    return {"message": "Item berhasil dihapus"}
