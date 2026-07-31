# CarbonatiX ERP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor existing FastAPI backend and Streamlit client to implement the CarbonatiX ERP API schema with proper API layer architecture.

**Architecture:** Backend uses versioned REST API under `/api/v1/`, MongoDB collections per domain, JWT auth with role-based access. Client refactored from direct MongoDB to HTTP API calls.

**Tech Stack:** FastAPI, PyMongo, Pydantic, Streamlit, httpx, python-multipart, JWT (PyJWT)

## Global Constraints

- API routes must be under `/api/v1/` prefix
- MongoDB collections: users, nodes, node_parameters, documents, extracted_data, scans, models
- JWT token stored in Streamlit session state, sent as Bearer header
- File uploads stored in `server/uploads/` directory
- Role hierarchy: superadmin > admin > operator > viewer
- Pagination default: page=1, page_size=20

---

### Task 1: Add dependencies and update config

**Files:**
- Modify: `requirements.txt`
- Modify: `server/config.py`

**Interfaces:**
- Consumes: existing config structure
- Produces: updated Settings class with new fields

- [ ] **Step 1: Add new dependencies to requirements.txt**

```txt
httpx>=0.27.0
python-multipart>=0.0.9
```

- [ ] **Step 2: Run pip install**

```bash
pip install httpx python-multipart
```

- [ ] **Step 3: Update config.py with new settings**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MONGODB_URI: str
    MONGODB_DB_NAME: str
    JWT_SECRET_KEY: str
    UPLOAD_DIR: str = str(Path(__file__).parent.parent / "uploads")


settings = Settings()
```

- [ ] **Step 4: Create uploads directory**

```bash
mkdir -p server/uploads
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt server/config.py server/uploads/
git commit -m "feat: add httpx, multipart deps and upload config"
```

---

### Task 2: Create Pydantic models

**Files:**
- Modify: `server/models/__init__.py`
- Create: `server/models/user.py`
- Create: `server/models/node.py`
- Create: `server/models/document.py`
- Create: `server/models/scan.py`
- Create: `server/models/model.py`

**Interfaces:**
- Consumes: existing user model
- Produces: Pydantic schemas for all API requests/responses

- [ ] **Step 1: Update models/__init__.py**

```python
from .user import *
from .node import *
from .document import *
from .scan import *
from .model import *
```

- [ ] **Step 2: Create user models (server/models/user.py)**

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    superadmin = "superadmin"
    operator = "operator"
    viewer = "viewer"


class UserStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    facility_id: str
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    facility_id: Optional[str] = None
    is_active: Optional[bool] = None


class UserApproval(BaseModel):
    status: UserStatus
    approved_by: str
    approved_at: datetime


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    facility_id: str
    phone_number: Optional[str] = None
    is_active: bool
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class UserListParams(BaseModel):
    role: Optional[UserRole] = None
    facility_id: Optional[str] = None
    status: Optional[UserStatus] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20
```

- [ ] **Step 3: Create node models (server/models/node.py)**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from enum import Enum


class NodeType(str, Enum):
    furnace = "furnace"
    converter = "converter"
    casting = "casting"


class NodeStatus(str, Enum):
    active = "active"
    idle = "idle"
    maintenance = "maintenance"


class Granularity(str, Enum):
    raw = "raw"
    hourly = "hourly"
    daily = "daily"


class NodeCreate(BaseModel):
    node_id: str
    node_name: str
    facility_id: str
    line: str
    latitude: float
    longitude: float
    node_type: NodeType
    status: NodeStatus


class NodeUpdate(BaseModel):
    node_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[NodeStatus] = None
    node_type: Optional[NodeType] = None


class NodeParameterInput(BaseModel):
    timestamp: datetime
    electrode_load: Optional[float] = None
    tap_temperature: Optional[float] = None
    power_draw: Optional[float] = None
    hourly_emissions: Optional[float] = None
    ptbae_pu_cap_contribution: Optional[float] = None
    ore_input_vol: Optional[float] = None
    avg_moisture: Optional[float] = None
    nickel_grade: Optional[float] = None
    total_power_draw: Optional[float] = None
    scope_process: Optional[float] = None
    scope_grid: Optional[float] = None
    current_intensity: Optional[float] = None


class NodeParameterResponse(NodeParameterInput):
    id: str
    node_id: str


class NodeResponse(BaseModel):
    id: str
    node_id: str
    node_name: str
    facility_id: str
    line: str
    latitude: float
    longitude: float
    node_type: NodeType
    status: NodeStatus
    created_at: datetime
    updated_at: datetime


class NodeListParams(BaseModel):
    facility_id: Optional[str] = None
    status: Optional[NodeStatus] = None
    node_type: Optional[NodeType] = None
    page: int = 1
    page_size: int = 20


class NodeParameterQuery(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    granularity: Granularity = Granularity.raw
```

- [ ] **Step 4: Create document models (server/models/document.py)**

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class DocumentType(str, Enum):
    spe_grk = "spe_grk"
    srn_ppi = "srn_ppi"
    lcam = "lcam"
    invoice = "invoice"
    permit = "permit"
    other = "other"


class ExtractionMode(str, Enum):
    auto = "auto"
    manual = "manual"


class ExtractionStatus(str, Enum):
    success = "success"
    partial = "partial"
    failed = "failed"


class DocumentCreate(BaseModel):
    document_type: DocumentType
    facility_id: str
    uploaded_by: str
    tags: Optional[List[str]] = None


class DocumentExtract(BaseModel):
    extraction_mode: ExtractionMode
    extract_fields: Optional[List[str]] = None


class ExtractedDataResponse(BaseModel):
    document_id: str
    extracted_at: datetime
    confidence_score: float
    fields: Dict[str, Any]
    raw_text: str
    status: ExtractionStatus


class DocumentResponse(BaseModel):
    id: str
    filename: str
    document_type: DocumentType
    facility_id: str
    uploaded_by: str
    tags: Optional[List[str]] = None
    status: str
    created_at: datetime


class DocumentListParams(BaseModel):
    facility_id: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20
```

- [ ] **Step 5: Create scan models (server/models/scan.py)**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ScanCreate(BaseModel):
    facility_id: str
    node_id: Optional[str] = None
    scan_name: str
    captured_at: Optional[datetime] = None
    captured_by: str


class ScanResponse(BaseModel):
    id: str
    scan_name: str
    facility_id: str
    node_id: Optional[str] = None
    filename: str
    file_format: str
    captured_at: Optional[datetime] = None
    captured_by: str
    created_at: datetime


class ScanListParams(BaseModel):
    facility_id: Optional[str] = None
    node_id: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20


class ScanFileFormat(str, Enum):
    glb = "glb"
    obj = "obj"
    ply = "ply"
```

- [ ] **Step 6: Create model schemas (server/models/model.py)**

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ModelType(str, Enum):
    emission_prediction = "emission_prediction"
    what_if_simulation = "what_if_simulation"


class ModelStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    training = "training"


class ModelResponse(BaseModel):
    id: str
    model_name: str
    model_type: ModelType
    facility_id: str
    status: ModelStatus
    created_at: datetime


class ModelListParams(BaseModel):
    facility_id: Optional[str] = None
    model_type: Optional[ModelType] = None
    status: Optional[ModelStatus] = None


class SimulationRequest(BaseModel):
    facility_id: str
    shift_coal_to_hydro_pct: int  # 0-100
    production_capacity_overdrive_pct: int  # 50-150
    ore_quality_moisture_ni_grade_pct: int  # 0-100
    inject_bio_coke_reductant: bool


class SimulationResult(BaseModel):
    facility_id: str
    baseline_emissions: float
    simulated_emissions: float
    reduction_pct: float
    intensity_change: float
    recommendations: list[str]
```

- [ ] **Step 7: Commit**

```bash
git add server/models/
git commit -m "feat: add Pydantic schemas for all API endpoints"
```

---

### Task 3: Create user router

**Files:**
- Create: `server/routers/users.py`
- Modify: `server/main.py`

**Interfaces:**
- Consumes: user models, database dependency
- Produces: `/api/v1/users` endpoints

- [ ] **Step 1: Create users router (server/routers/users.py)**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from ..deps import get_db, get_current_user
from ..models.user import (
    UserCreate, UserUpdate, UserApproval, UserResponse,
    UserListParams, UserRole, UserStatus
)
from ..auth import hash_password
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(req: UserCreate, db=Depends(get_db)):
    # Check uniqueness
    if db.users.find_one({"username": req.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.users.find_one({"email": req.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    now = datetime.utcnow()
    user_doc = {
        "username": req.username,
        "email": req.email,
        "password": hash_password(req.password),
        "full_name": req.full_name,
        "role": req.role.value,
        "facility_id": req.facility_id,
        "phone_number": req.phone_number,
        "is_active": True,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }
    result = db.users.insert_one(user_doc)
    return UserResponse(
        id=str(result.inserted_id),
        **{k: v for k, v in user_doc.items() if k != "password"}
    )


@router.get("/", response_model=dict)
def list_users(
    role: Optional[UserRole] = None,
    facility_id: Optional[str] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = {}
    if role:
        query["role"] = role.value
    if facility_id:
        query["facility_id"] = facility_id
    if status:
        query["status"] = status.value
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]

    total = db.users.count_documents(query)
    skip = (page - 1) * page_size
    users = list(db.users.find(query).skip(skip).limit(page_size))

    return {
        "items": [
            UserResponse(
                id=str(u["_id"]),
                username=u["username"],
                email=u["email"],
                full_name=u["full_name"],
                role=u["role"],
                facility_id=u["facility_id"],
                phone_number=u.get("phone_number"),
                is_active=u["is_active"],
                status=u["status"],
                created_at=u["created_at"],
                updated_at=u["updated_at"],
            )
            for u in users
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, req: UserUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()
    result = db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(result["_id"]),
        username=result["username"],
        email=result["email"],
        full_name=result["full_name"],
        role=result["role"],
        facility_id=result["facility_id"],
        phone_number=result.get("phone_number"),
        is_active=result["is_active"],
        status=result["status"],
        created_at=result["created_at"],
        updated_at=result["updated_at"],
    )


@router.put("/{user_id}/approve", response_model=UserResponse)
def approve_user(user_id: str, req: UserApproval, db=Depends(get_db), current_user=Depends(get_current_user)):
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can approve users")

    update_data = {
        "status": req.status.value,
        "approved_by": req.approved_by,
        "approved_at": req.approved_at,
        "updated_at": datetime.utcnow(),
    }
    result = db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(result["_id"]),
        username=result["username"],
        email=result["email"],
        full_name=result["full_name"],
        role=result["role"],
        facility_id=result["facility_id"],
        phone_number=result.get("phone_number"),
        is_active=result["is_active"],
        status=result["status"],
        created_at=result["created_at"],
        updated_at=result["updated_at"],
    )
```

- [ ] **Step 2: Register router in main.py**

Add import and include_router:
```python
from .routers import auth, items, admin, users
# ...
app.include_router(users.router)
```

- [ ] **Step 3: Commit**

```bash
git add server/routers/users.py server/main.py
git commit -m "feat: add users CRUD router with approval endpoint"
```

---

### Task 4: Create node router

**Files:**
- Create: `server/routers/nodes.py`
- Modify: `server/main.py`

**Interfaces:**
- Consumes: node models, database dependency
- Produces: `/api/v1/nodes` endpoints

- [ ] **Step 1: Create nodes router (server/routers/nodes.py)**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from ..deps import get_db, get_current_user
from ..models.node import (
    NodeCreate, NodeUpdate, NodeParameterInput, NodeParameterQuery,
    NodeResponse, NodeParameterResponse, NodeListParams,
    NodeType, NodeStatus, Granularity
)
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/v1/nodes", tags=["nodes"])


@router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(req: NodeCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    if db.nodes.find_one({"node_id": req.node_id}):
        raise HTTPException(status_code=400, detail="Node ID already exists")

    now = datetime.utcnow()
    node_doc = {
        "node_id": req.node_id,
        "node_name": req.node_name,
        "facility_id": req.facility_id,
        "line": req.line,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "node_type": req.node_type.value,
        "status": req.status.value,
        "created_at": now,
        "updated_at": now,
    }
    result = db.nodes.insert_one(node_doc)
    return NodeResponse(id=str(result.inserted_id), **node_doc)


@router.get("/", response_model=dict)
def list_nodes(
    facility_id: Optional[str] = None,
    status: Optional[NodeStatus] = None,
    node_type: Optional[NodeType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = {}
    if facility_id:
        query["facility_id"] = facility_id
    if status:
        query["status"] = status.value
    if node_type:
        query["node_type"] = node_type.value

    total = db.nodes.count_documents(query)
    skip = (page - 1) * page_size
    nodes = list(db.nodes.find(query).skip(skip).limit(page_size))

    return {
        "items": [NodeResponse(id=str(n["_id"]), **{k: v for k, v in n.items() if k != "_id"}) for n in nodes],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: str, req: NodeUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    update_data = {k: v.value if hasattr(v, "value") else v for k, v in req.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()
    result = db.nodes.find_one_and_update(
        {"_id": ObjectId(node_id)},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Node not found")

    return NodeResponse(id=str(result["_id"]), **{k: v for k, v in result.items() if k != "_id"})


@router.post("/{node_id}/parameters", response_model=NodeParameterResponse, status_code=status.HTTP_201_CREATED)
def create_node_parameter(node_id: str, req: NodeParameterInput, db=Depends(get_db), current_user=Depends(get_current_user)):
    node = db.nodes.find_one({"_id": ObjectId(node_id)})
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    param_doc = {
        "node_id": node_id,
        "timestamp": req.timestamp,
        "electrode_load": req.electrode_load,
        "tap_temperature": req.tap_temperature,
        "power_draw": req.power_draw,
        "hourly_emissions": req.hourly_emissions,
        "ptbae_pu_cap_contribution": req.ptbae_pu_cap_contribution,
        "ore_input_vol": req.ore_input_vol,
        "avg_moisture": req.avg_moisture,
        "nickel_grade": req.nickel_grade,
        "total_power_draw": req.total_power_draw,
        "scope_process": req.scope_process,
        "scope_grid": req.scope_grid,
        "current_intensity": req.current_intensity,
    }
    result = db.node_parameters.insert_one(param_doc)
    return NodeParameterResponse(id=str(result.inserted_id), **param_doc)


@router.get("/{node_id}/parameters", response_model=dict)
def get_node_parameters(
    node_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    granularity: Granularity = Granularity.raw,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = {"node_id": node_id}
    if date_from:
        query["timestamp"] = {"$gte": datetime.fromisoformat(date_from)}
    if date_to:
        if "timestamp" in query:
            query["timestamp"]["$lte"] = datetime.fromisoformat(date_to)
        else:
            query["timestamp"] = {"$lte": datetime.fromisoformat(date_to)}

    total = db.node_parameters.count_documents(query)
    skip = (page - 1) * page_size
    params = list(db.node_parameters.find(query).sort("timestamp", -1).skip(skip).limit(page_size))

    return {
        "items": [NodeParameterResponse(id=str(p["_id"]), **{k: v for k, v in p.items() if k != "_id"}) for p in params],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
```

- [ ] **Step 2: Register router in main.py**

Add import and include_router:
```python
from .routers import auth, items, admin, users, nodes
# ...
app.include_router(nodes.router)
```

- [ ] **Step 3: Commit**

```bash
git add server/routers/nodes.py server/main.py
git commit -m "feat: add nodes CRUD and parameters router"
```

---

### Task 5: Create document router

**Files:**
- Create: `server/routers/documents.py`
- Modify: `server/main.py`

**Interfaces:**
- Consumes: document models, database dependency, file upload
- Produces: `/api/v1/documents` endpoints

- [ ] **Step 1: Create documents router (server/routers/documents.py)**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import Optional
from ..deps import get_db, get_current_user
from ..models.document import (
    DocumentCreate, DocumentExtract, ExtractedDataResponse,
    DocumentResponse, DocumentListParams, DocumentType, ExtractionMode
)
from ..config import settings
from bson import ObjectId
from datetime import datetime
import os
import uuid

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Query(...),
    facility_id: str = Query(...),
    uploaded_by: str = Query(...),
    tags: Optional[str] = Query(None),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    upload_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    now = datetime.utcnow()
    doc_doc = {
        "filename": unique_filename,
        "original_filename": file.filename,
        "document_type": document_type.value,
        "facility_id": facility_id,
        "uploaded_by": uploaded_by,
        "tags": tags.split(",") if tags else [],
        "status": "uploaded",
        "file_size": len(content),
        "created_at": now,
    }
    result = db.documents.insert_one(doc_doc)
    return DocumentResponse(id=str(result.inserted_id), **{k: v for k, v in doc_doc.items() if k != "file_size"})


@router.get("/", response_model=dict)
def list_documents(
    facility_id: Optional[str] = None,
    document_type: Optional[DocumentType] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = {}
    if facility_id:
        query["facility_id"] = facility_id
    if document_type:
        query["document_type"] = document_type.value
    if status:
        query["status"] = status
    if date_from:
        query["created_at"] = {"$gte": datetime.fromisoformat(date_from)}
    if date_to:
        if "created_at" in query:
            query["created_at"]["$lte"] = datetime.fromisoformat(date_to)
        else:
            query["created_at"] = {"$lte": datetime.fromisoformat(date_to)}

    total = db.documents.count_documents(query)
    skip = (page - 1) * page_size
    docs = list(db.documents.find(query).sort("created_at", -1).skip(skip).limit(page_size))

    return {
        "items": [
            DocumentResponse(
                id=str(d["_id"]),
                filename=d["original_filename"],
                document_type=d["document_type"],
                facility_id=d["facility_id"],
                uploaded_by=d["uploaded_by"],
                tags=d.get("tags"),
                status=d["status"],
                created_at=d["created_at"],
            )
            for d in docs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{doc_id}/extract", response_model=ExtractedDataResponse)
def extract_document(
    doc_id: str,
    req: DocumentExtract,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc = db.documents.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extracted_data = {
        "document_id": doc_id,
        "extracted_at": datetime.utcnow(),
        "confidence_score": 0.85,
        "fields": {
            "title": "Sample Extracted Title",
            "date": datetime.utcnow().isoformat(),
            "amount": 1000000,
        },
        "raw_text": "Sample raw text from OCR extraction...",
        "status": "success",
    }

    db.extracted_data.insert_one({**extracted_data, "document_id": doc_id})
    db.documents.update_one({"_id": ObjectId(doc_id)}, {"$set": {"status": "extracted"}})

    return ExtractedDataResponse(**extracted_data)


@router.get("/{doc_id}/extracted-data", response_model=ExtractedDataResponse)
def get_extracted_data(doc_id: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    data = db.extracted_data.find_one({"document_id": doc_id})
    if not data:
        raise HTTPException(status_code=404, detail="Extracted data not found")

    return ExtractedDataResponse(
        document_id=data["document_id"],
        extracted_at=data["extracted_at"],
        confidence_score=data["confidence_score"],
        fields=data["fields"],
        raw_text=data["raw_text"],
        status=data["status"],
    )
```

- [ ] **Step 2: Register router in main.py**

Add import and include_router:
```python
from .routers import auth, items, admin, users, nodes, documents
# ...
app.include_router(documents.router)
```

- [ ] **Step 3: Commit**

```bash
git add server/routers/documents.py server/main.py
git commit -m "feat: add documents upload and extraction router"
```

---

### Task 6: Create scan router

**Files:**
- Create: `server/routers/scans.py`
- Modify: `server/main.py`

**Interfaces:**
- Consumes: scan models, database dependency, file upload
- Produces: `/api/v1/scans` endpoints

- [ ] **Step 1: Create scans router (server/routers/scans.py)**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
from ..deps import get_db, get_current_user
from ..models.scan import ScanCreate, ScanResponse, ScanListParams, ScanFileFormat
from ..config import settings
from bson import ObjectId
from datetime import datetime
import os
import uuid

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def upload_scan(
    file: UploadFile = File(...),
    facility_id: str = Query(...),
    node_id: Optional[str] = Query(None),
    scan_name: str = Query(...),
    captured_at: Optional[str] = Query(None),
    captured_by: str = Query(...),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".glb", ".obj", ".ply"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Must be .glb, .obj, or .ply")

    unique_filename = f"{uuid.uuid4()}{file_ext}"
    upload_path = os.path.join(settings.UPLOAD_DIR, "scans", unique_filename)

    os.makedirs(os.path.join(settings.UPLOAD_DIR, "scans"), exist_ok=True)
    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    now = datetime.utcnow()
    scan_doc = {
        "scan_name": scan_name,
        "facility_id": facility_id,
        "node_id": node_id,
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_format": file_ext.lstrip("."),
        "captured_at": datetime.fromisoformat(captured_at) if captured_at else now,
        "captured_by": captured_by,
        "file_size": len(content),
        "created_at": now,
    }
    result = db.scans.insert_one(scan_doc)
    return ScanResponse(id=str(result.inserted_id), **{k: v for k, v in scan_doc.items() if k != "file_size"})


@router.get("/", response_model=dict)
def list_scans(
    facility_id: Optional[str] = None,
    node_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = {}
    if facility_id:
        query["facility_id"] = facility_id
    if node_id:
        query["node_id"] = node_id
    if date_from:
        query["created_at"] = {"$gte": datetime.fromisoformat(date_from)}
    if date_to:
        if "created_at" in query:
            query["created_at"]["$lte"] = datetime.fromisoformat(date_to)
        else:
            query["created_at"] = {"$lte": datetime.fromisoformat(date_to)}

    total = db.scans.count_documents(query)
    skip = (page - 1) * page_size
    scans = list(db.scans.find(query).sort("created_at", -1).skip(skip).limit(page_size))

    return {
        "items": [
            ScanResponse(
                id=str(s["_id"]),
                scan_name=s["scan_name"],
                facility_id=s["facility_id"],
                node_id=s.get("node_id"),
                filename=s["original_filename"],
                file_format=s["file_format"],
                captured_at=s.get("captured_at"),
                captured_by=s["captured_by"],
                created_at=s["created_at"],
            )
            for s in scans
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{scan_id}/file")
def download_scan(
    scan_id: str,
    format: Optional[ScanFileFormat] = None,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    scan = db.scans.find_one({"_id": ObjectId(scan_id)})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    file_path = os.path.join(settings.UPLOAD_DIR, "scans", scan["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Scan file not found on disk")

    return FileResponse(
        path=file_path,
        filename=scan["original_filename"],
        media_type="application/octet-stream",
    )


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scan(scan_id: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    scan = db.scans.find_one({"_id": ObjectId(scan_id)})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    file_path = os.path.join(settings.UPLOAD_DIR, "scans", scan["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

    db.scans.delete_one({"_id": ObjectId(scan_id)})
```

- [ ] **Step 2: Register router in main.py**

Add import and include_router:
```python
from .routers import auth, items, admin, users, nodes, documents, scans
# ...
app.include_router(scans.router)
```

- [ ] **Step 3: Commit**

```bash
git add server/routers/scans.py server/main.py
git commit -m "feat: add 3D scans upload and download router"
```

---

### Task 7: Create models router

**Files:**
- Create: `server/routers/models.py`
- Modify: `server/main.py`

**Interfaces:**
- Consumes: model schemas, database dependency
- Produces: `/api/v1/models` endpoints

- [ ] **Step 1: Create models router (server/routers/models.py)**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..deps import get_db, get_current_user
from ..models.model import (
    ModelResponse, ModelListParams, SimulationRequest, SimulationResult,
    ModelType, ModelStatus
)
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("/", response_model=dict)
def list_models(
    facility_id: Optional[str] = None,
    model_type: Optional[ModelType] = None,
    status: Optional[ModelStatus] = None,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = {}
    if facility_id:
        query["facility_id"] = facility_id
    if model_type:
        query["model_type"] = model_type.value
    if status:
        query["status"] = status.value

    models = list(db.models.find(query))
    return {
        "items": [
            ModelResponse(
                id=str(m["_id"]),
                model_name=m["model_name"],
                model_type=m["model_type"],
                facility_id=m["facility_id"],
                status=m["status"],
                created_at=m["created_at"],
            )
            for m in models
        ],
        "total": len(models),
    }


@router.post("/simulate", response_model=SimulationResult)
def simulate(req: SimulationRequest, db=Depends(get_db), current_user=Depends(get_current_user)):
    baseline_emissions = 1000.0

    reduction_factor = req.shift_coal_to_hydro_pct / 100 * 0.3
    overdrive_factor = (req.production_capacity_overdrive_pct - 100) / 100 * 0.2
    quality_factor = req.ore_quality_moisture_ni_grade_pct / 100 * 0.1
    bio_factor = 0.05 if req.inject_bio_coke_reductant else 0

    total_reduction = reduction_factor + overdrive_factor + quality_factor + bio_factor
    simulated_emissions = baseline_emissions * (1 - total_reduction)

    return SimulationResult(
        facility_id=req.facility_id,
        baseline_emissions=baseline_emissions,
        simulated_emissions=round(simulated_emissions, 2),
        reduction_pct=round(total_reduction * 100, 2),
        intensity_change=round(total_reduction * 0.8, 2),
        recommendations=[
            "Shift coal to hydro shows significant reduction",
            "Production overdrive increases emissions but may offset per-unit",
            "Higher ore quality reduces processing emissions",
            "Bio-coke injection provides additional 5% reduction",
        ],
    )
```

- [ ] **Step 2: Register router in main.py**

Add import and include_router:
```python
from .routers import auth, items, admin, users, nodes, documents, scans, models
# ...
app.include_router(models.router)
```

- [ ] **Step 3: Commit**

```bash
git add server/routers/models.py server/main.py
git commit -m "feat: add AI simulation models router"
```

---

### Task 8: Create API client for Streamlit

**Files:**
- Create: `client/api.py`

**Interfaces:**
- Consumes: FastAPI endpoints
- Produces: HTTP client wrapper functions

- [ ] **Step 1: Create API client (client/api.py)**

```python
import httpx
import streamlit as st
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8000/api/v1"


def get_headers() -> Dict[str, str]:
    token = st.session_state.get("token")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def login(username: str, password: str) -> Optional[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/../auth/login",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            return response.json()
        return None


async def register(username: str, name: str, password: str) -> tuple[bool, str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/../auth/register",
            json={"username": username, "name": name, "password": password},
        )
        return response.status_code == 200, response.json().get("message", "Error")


async def get_users(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/users/", headers=get_headers(), params=params)
        return response.json()


async def create_user(data: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/users/", headers=get_headers(), json=data)
        return response.json()


async def get_nodes(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nodes/", headers=get_headers(), params=params)
        return response.json()


async def create_node(data: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/nodes/", headers=get_headers(), json=data)
        return response.json()


async def get_node_parameters(node_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/nodes/{node_id}/parameters", headers=get_headers(), params=params)
        return response.json()


async def create_node_parameter(node_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/nodes/{node_id}/parameters", headers=get_headers(), json=data)
        return response.json()


async def get_documents(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/documents/", headers=get_headers(), params=params)
        return response.json()


async def upload_document(file, document_type: str, facility_id: str, uploaded_by: str, tags: Optional[str] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        files = {"file": (file.name, file.getvalue())}
        params = {
            "document_type": document_type,
            "facility_id": facility_id,
            "uploaded_by": uploaded_by,
        }
        if tags:
            params["tags"] = tags
        response = await client.post(
            f"{BASE_URL}/documents/",
            headers={"Authorization": f"Bearer {st.session_state.get('token', '')}"},
            files=files,
            params=params,
        )
        return response.json()


async def get_scans(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/scans/", headers=get_headers(), params=params)
        return response.json()


async def simulate(data: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/models/simulate", headers=get_headers(), json=data)
        return response.json()
```

- [ ] **Step 2: Commit**

```bash
git add client/api.py
git commit -m "feat: add HTTP API client for Streamlit"
```

---

### Task 9: Refactor Streamlit client

**Files:**
- Modify: `client/app.py`
- Create: `client/pages/1_nodes.py`
- Create: `client/pages/2_documents.py`
- Create: `client/pages/3_scans.py`
- Create: `client/pages/4_models.py`

**Interfaces:**
- Consumes: API client, existing auth logic
- Produces: Refactored Streamlit pages using API

- [ ] **Step 1: Refactor app.py to use API client**

Replace direct MongoDB calls with API calls in the login/register functions. Remove direct DB connection code.

- [ ] **Step 2: Create nodes page (client/pages/1_nodes.py)**

Add node monitoring dashboard with parameter input forms and time-series display.

- [ ] **Step 3: Create documents page (client/pages/2_documents.py)**

Add document upload and extraction interface.

- [ ] **Step 4: Create scans page (client/pages/3_scans.py)**

Add 3D scan upload and file download interface.

- [ ] **Step 5: Create models page (client/pages/4_models.py)**

Add AI simulation form with results display.

- [ ] **Step 6: Commit**

```bash
git add client/
git commit -m "feat: refactor Streamlit client to use FastAPI endpoints"
```

---

### Task 10: Update main.py with all routers

**Files:**
- Modify: `server/main.py`

**Interfaces:**
- Consumes: all routers
- Produces: Complete FastAPI app

- [ ] **Step 1: Update main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, items, admin, users, nodes, documents, scans, models

app = FastAPI(
    title="CarbonatiX ERP API",
    description="ERP system for nickel processing facility management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(nodes.router)
app.include_router(documents.router)
app.include_router(scans.router)
app.include_router(models.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

- [ ] **Step 2: Commit**

```bash
git add server/main.py
git commit -m "feat: register all API routers in main app"
```

---

### Task 11: Update requirements.txt

**Files:**
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: existing dependencies
- Produces: Updated requirements

- [ ] **Step 1: Update requirements.txt**

```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pymongo>=4.6.0
bcrypt>=4.1.0
PyJWT>=2.8.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
httpx>=0.27.0
python-multipart>=0.0.9
pydantic[email]>=2.5.0
```

- [ ] **Step 2: Commit**

```bash
git add requirements.txt
git commit -m "feat: add httpx and python-multipart dependencies"
```

---

### Task 12: Test the implementation

**Files:**
- None (testing only)

**Interfaces:**
- Consumes: All implemented routers and client
- Produces: Verified working system

- [ ] **Step 1: Start the FastAPI server**

```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- [ ] **Step 2: Test API endpoints**

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "name": "Admin", "password": "admin123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

- [ ] **Step 3: Start Streamlit client**

```bash
cd client
streamlit run app.py
```

- [ ] **Step 4: Verify Streamlit connects to API**

Open browser to http://localhost:8501 and verify login/register works via API.

- [ ] **Step 5: Final commit**

```bash
git add .
git commit -m "feat: complete CarbonatiX ERP refactor with all endpoints"
```
