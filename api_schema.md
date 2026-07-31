# Streamlit Frontend - MongoDB Direct (Tanpa FastAPI)

## 1\. Users (`collection: users`)

|Operasi|Streamlit Page|Widget|MongoDB Query|
|-|-|-|-|
|List semua user|`pages/User\_Management.py`|`st.dataframe()`|`db.users.find()`|
|Tambah user|`pages/User\_Management.py`|`st.form()`|`db.users.insert\\\_one()`|
|Detail user|`pages/User\_Management.py`|`st.selectbox()` + detail|`db.users.find\\\_one({\\\_id: ...})`|
|Update user|`pages/User\_Management.py`|`st.form()` edit|`db.users.update\\\_one({\\\_id: ...})`|
|Hapus user|`pages/User\_Management.py`|`st.button("Hapus")`|`db.users.delete\\\_one({\\\_id: ...})`|
|Approve user|`pages/User\_Management.py`|`st.toggle()`|`db.users.update\\\_one({\\\_id: ...}, {role: "approved"})`|

\---

## 2\. Node Data - RKEF Process (`collection: nodes`)

|Operasi|Streamlit Page|Widget|MongoDB Query|
|-|-|-|-|
|List semua node|`pages/Node\_Data.py`|`st.dataframe()`|`db.nodes.find()`|
|Tambah node|`pages/Node\_Data.py`|`st.form()`|`db.nodes.insert\_one()`|
|Detail node|`pages/Node\_Data.py`|`st.selectbox()` + detail|`db.nodes.find\_one({\_id: ...})`|
|Update node|`pages/Node\_Data.py`|`st.form()` edit|`db.nodes.update\_one({\_id: ...})`|
|Hapus node|`pages/Node\_Data.py`|`st.button("Hapus")`|`db.nodes.delete\_one({\_id: ...})`|
|Input parameter|`pages/Node\_Data.py`|`st.form()` parameters|`db.nodes.update\_one({\_id: ...}, {$set: {parameters: ...}})`|
|Lihat parameter|`pages/Node\_Data.py`|`st.json()`|`db.nodes.find\_one({\_id: ...}, {parameters: 1})`|

\---

## 3\. Document Upload \& Extraction (`collection: documents`)

|Operasi|Streamlit Page|Widget|MongoDB Query|
|-|-|-|-|
|List dokumen|`pages/Documents.py`|`st.dataframe()`|`db.documents.find()`|
|Upload dokumen|`pages/Documents.py`|`st.file\\\_uploader()`|`db.documents.insert\\\_one()` + simpan file ke GridFS/disk|
|Detail dokumen|`pages/Documents.py`|`st.selectbox()` + detail|`db.documents.find\\\_one({\\\_id: ...})`|
|Hapus dokumen|`pages/Documents.py`|`st.button("Hapus")`|`db.documents.delete\\\_one({\\\_id: ...})` + hapus file|
|Ekstrak data|`pages/Documents.py`|`st.button("Ekstrak")`|Jalankan ekstraksi → simpan ke `db.extracted\\\_data.insert\\\_one()`|
|Lihat hasil ekstraksi|`pages/Documents.py`|`st.dataframe()`|`db.extracted\\\_data.find({doc\\\_id: ...})`|

\---

## 4\. 3D Models (`collection: models`)

|Operasi|Streamlit Page|Widget|MongoDB Query|
|-|-|-|-|
|List scan|`pages/3D\\\_Models.py`|`st.dataframe()`|`db.scans.find()`|
|Upload scan|`pages/3D\\\_Models.py`|`st.file\\\_uploader()`|`db.scans.insert\\\_one()` + simpan file ke GridFS/disk|
|Detail scan|`pages/3D\\\_Models.py`|`st.selectbox()` + detail|`db.scans.find\\\_one({\\\_id: ...})`|
|Hapus scan|`pages/3D\\\_Models.py`|`st.button("Hapus")`|`db.scans.delete\\\_one({\\\_id: ...})` + hapus file|
|Download file|`pages/3D\\\_Models.py`|`st.download\\\_button()`|Baca file dari disk → download|

\---

## Struktur Folder

```
client/
├── app.py                          # Login + Dashboard utama
├── .streamlit/
│   └── secrets.toml
├── pages/
│   ├── 1\\\_User\\\_Management.py
│   ├── 2\\\_Node\\\_Data.py
│   ├── 3\\\_Documents.py
│   └── 4\\\_3D\\\_Scans.py
└── utils/
    └── db.py                       # Koneksi MongoDB + helper functions

server/
├── db.py                           # Koneksi MongoDB
├── auth.py                         # Auth + JWT
└── models/
    └── ...
```

\---

## Flow Setiap Halaman

### User Management

```
1. Load users:     db.users.find()
2. Tampilkan:      st.dataframe()
3. Tambah user:    st.form() → db.users.insert\\\_one()
4. Edit user:      st.form() → db.users.update\\\_one({\\\_id: ...})
5. Hapus user:     st.button() → db.users.delete\\\_one({\\\_id: ...})
6. Approve user:   st.toggle() → db.users.update\\\_one({\\\_id: ...}, {role: "approved"})
```

### Node Data (RKEF)

```
1. Load nodes:     db.nodes.find()
2. Tampilkan:      st.dataframe()
3. Tambah node:    st.form() → db.nodes.insert\\\_one()
4. Edit node:      st.form() → db.nodes.update\\\_one({\\\_id: ...})
5. Hapus node:     st.button() → db.nodes.delete\\\_one({\\\_id: ...})
6. Input parameter: st.form() → db.nodes.update\\\_one({\\\_id: ...}, {$set: {parameters: ...}})
7. Lihat parameter: db.nodes.find\\\_one({\\\_id: ...}, {parameters: 1})
```

### Document Upload

```
1. Load documents: db.documents.find()
2. Tampilkan:      st.dataframe()
3. Upload file:    st.file\\\_uploader() → db.documents.insert\\\_one() + save file
4. Ekstrak data:   st.button() → run extraction → db.extracted\\\_data.insert\\\_one()
5. Lihat hasil:    db.extracted\\\_data.find({doc\\\_id: ...})
6. Hapus:          st.button() → db.documents.delete\\\_one() + delete file
```

### 3D Scan

```
1. Load scans:     db.scans.find()
2. Tampilkan:      st.dataframe()
3. Upload file:    st.file\\\_uploader() → db.scans.insert\\\_one() + save file
4. Download file:  st.download\\\_button() → read file from disk
5. Hapus:          st.button() → db.scans.delete\\\_one() + delete file
```

\---

## Contoh Kode - api\_client.py

```python
import streamlit as st
from bson import ObjectId

db = st.session\\\_state.db

# ==================== USERS ====================
def get\\\_users():
    return list(db.users.find({}, {"\\\_id": 0}))

def add\\\_user(data: dict):
    return db.users.insert\\\_one(data)

def update\\\_user(user\\\_id: str, data: dict):
    return db.users.update\\\_one({"\\\_id": ObjectId(user\\\_id)}, {"$set": data})

def delete\\\_user(user\\\_id: str):
    return db.users.delete\\\_one({"\\\_id": ObjectId(user\\\_id)})

def approve\\\_user(user\\\_id: str):
    return db.users.update\\\_one({"\\\_id": ObjectId(user\\\_id)}, {"$set": {"role": "approved"}})

# ==================== NODES ====================
def get\\\_nodes():
    return list(db.nodes.find({}, {"\\\_id": 0}))

def add\\\_node(data: dict):
    return db.nodes.insert\\\_one(data)

def update\\\_node(node\\\_id: str, data: dict):
    return db.nodes.update\\\_one({"\\\_id": ObjectId(node\\\_id)}, {"$set": data})

def delete\\\_node(node\\\_id: str):
    return db.nodes.delete\\\_one({"\\\_id": ObjectId(node\\\_id)})

def set\\\_node\\\_parameters(node\\\_id: str, parameters: dict):
    return db.nodes.update\\\_one({"\\\_id": ObjectId(node\\\_id)}, {"$set": {"parameters": parameters}})

def get\\\_node\\\_parameters(node\\\_id: str):
    node = db.nodes.find\\\_one({"\\\_id": ObjectId(node\\\_id)}, {"parameters": 1})
    return node.get("parameters", {}) if node else {}

# ==================== DOCUMENTS ====================
def get\\\_documents():
    return list(db.documents.find({}, {"\\\_id": 0}))

def add\\\_document(data: dict):
    return db.documents.insert\\\_one(data)

def delete\\\_document(doc\\\_id: str):
    return db.documents.delete\\\_one({"\\\_id": ObjectId(doc\\\_id)})

def extract\\\_document(doc\\\_id: str):
    # Jalankan ekstraksi data dari dokumen
    pass

def get\\\_extracted\\\_data(doc\\\_id: str):
    return list(db.extracted\\\_data.find({"doc\\\_id": doc\\\_id}, {"\\\_id": 0}))

# ==================== SCANS ====================
def get\\\_scans():
    return list(db.scans.find({}, {"\\\_id": 0}))

def add\\\_scan(data: dict):
    return db.scans.insert\\\_one(data)

def delete\\\_scan(scan\\\_id: str):
    return db.scans.delete\\\_one({"\\\_id": ObjectId(scan\\\_id)})
```

