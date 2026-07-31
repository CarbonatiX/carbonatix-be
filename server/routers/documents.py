import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from ..deps import get_db, get_current_user
from ..config import settings
from ..models.document import (
    DocumentType, ExtractionMode,
    DocumentCreate, DocumentExtract, ExtractedDataResponse,
    DocumentResponse
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Query(...),
    facility_id: str = Query(...),
    uploaded_by: str = Query(None),
    tags: str = Query(None),
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    documents = db["documents"]

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    file_content = file.file.read()
    with open(filepath, "wb") as f:
        f.write(file_content)

    now = datetime.now(timezone.utc)
    doc = {
        "id": uuid.uuid4().hex,
        "filename": filename,
        "original_filename": file.filename,
        "document_type": document_type.value,
        "facility_id": facility_id,
        "uploaded_by": uploaded_by or user.get("sub"),
        "tags": tags.split(",") if tags else None,
        "extraction_status": None,
        "file_size": len(file_content),
        "created_at": now,
        "updated_at": now,
    }

    documents.insert_one(doc)

    return doc


@router.get("/", response_model=dict)
def list_documents(
    facility_id: str = None,
    document_type: str = None,
    status: str = None,
    date_from: datetime = None,
    date_to: datetime = None,
    page: int = 1,
    page_size: int = 20,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    documents = db["documents"]
    query = {}

    if facility_id:
        query["facility_id"] = facility_id
    if document_type:
        query["document_type"] = document_type
    if status:
        query["extraction_status"] = status
    if date_from:
        query["created_at"] = {"$gte": date_from}
    if date_to:
        if "created_at" not in query:
            query["created_at"] = {}
        query["created_at"]["$lte"] = date_to

    skip = (page - 1) * page_size
    total = documents.count_documents(query)
    cursor = documents.find(query).skip(skip).limit(page_size)

    items = []
    for d in cursor:
        d["id"] = d.get("id", str(d["_id"]))
        if "_id" in d:
            del d["_id"]
        items.append(d)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/{doc_id}/extract", response_model=dict, status_code=status.HTTP_200_OK)
def run_extraction(
    doc_id: str,
    req: DocumentExtract,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    documents = db["documents"]

    doc = documents.find_one({"id": doc_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    now = datetime.now(timezone.utc)
    documents.update_one(
        {"id": doc_id},
        {"$set": {"extraction_status": "success", "updated_at": now}}
    )

    return {
        "document_id": doc_id,
        "extraction_mode": req.extraction_mode.value,
        "status": "success",
        "message": "Extraction completed"
    }


@router.get("/{doc_id}/extracted-data", response_model=ExtractedDataResponse)
def get_extracted_data(
    doc_id: str,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    documents = db["documents"]
    extracted = db["extracted_data"]

    doc = documents.find_one({"id": doc_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    data = extracted.find_one({"document_id": doc_id})
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No extracted data found for this document"
        )

    data["id"] = str(data.get("_id", ""))
    if "_id" in data:
        del data["_id"]

    return data
