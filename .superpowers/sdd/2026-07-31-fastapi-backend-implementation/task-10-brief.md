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
