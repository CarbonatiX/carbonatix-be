import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from ..deps import get_db, get_current_user
from ..config import settings
from ..models.scan import (
    ScanFileFormat,
    ScanCreate, ScanResponse, ScanListParams, ScanFileQuery
)

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])

ALLOWED_EXTENSIONS = {".glb", ".obj", ".ply"}


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def upload_scan(
    file: UploadFile = File(...),
    facility_id: str = Query(...),
    node_id: str = Query(None),
    scan_name: str = Query(...),
    captured_at: datetime = Query(None),
    captured_by: str = Query(None),
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    scans = db["scans"]

    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    file_content = file.file.read()
    with open(filepath, "wb") as f:
        f.write(file_content)

    now = datetime.now(timezone.utc)
    scan = {
        "id": uuid.uuid4().hex,
        "scan_name": scan_name,
        "facility_id": facility_id,
        "node_id": node_id,
        "file_format": ext.lstrip("."),
        "filename": filename,
        "original_filename": file.filename,
        "file_size": len(file_content),
        "captured_at": captured_at,
        "captured_by": captured_by or user.get("sub"),
        "created_at": now,
        "updated_at": now,
    }

    scans.insert_one(scan)

    return scan


@router.get("/", response_model=dict)
def list_scans(
    facility_id: str = None,
    node_id: str = None,
    date_from: datetime = None,
    date_to: datetime = None,
    page: int = 1,
    page_size: int = 20,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    scans = db["scans"]
    query = {}

    if facility_id:
        query["facility_id"] = facility_id
    if node_id:
        query["node_id"] = node_id
    if date_from:
        query["created_at"] = {"$gte": date_from}
    if date_to:
        if "created_at" not in query:
            query["created_at"] = {}
        query["created_at"]["$lte"] = date_to

    skip = (page - 1) * page_size
    total = scans.count_documents(query)
    cursor = scans.find(query).skip(skip).limit(page_size)

    items = []
    for s in cursor:
        s["id"] = s.get("id", str(s["_id"]))
        if "_id" in s:
            del s["_id"]
        items.append(s)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{scan_id}/file")
def download_scan_file(
    scan_id: str,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    scans = db["scans"]

    scan = scans.find_one({"id": scan_id})
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    filepath = os.path.join(settings.UPLOAD_DIR, scan["filename"])
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan file not found on disk"
        )

    media_type_map = {
        "glb": "model/gltf-binary",
        "obj": "text/plain",
        "ply": "application/octet-stream",
    }
    media_type = media_type_map.get(scan.get("file_format"), "application/octet-stream")

    return FileResponse(
        path=filepath,
        filename=scan.get("original_filename", scan["filename"]),
        media_type=media_type,
    )


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scan(
    scan_id: str,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    scans = db["scans"]

    scan = scans.find_one({"id": scan_id})
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    filepath = os.path.join(settings.UPLOAD_DIR, scan["filename"])
    if os.path.exists(filepath):
        os.remove(filepath)

    scans.delete_one({"id": scan_id})

    return None
