from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ScanFileFormat(str, Enum):
    glb = "glb"
    obj = "obj"
    ply = "ply"


class ScanCreate(BaseModel):
    facility_id: str
    node_id: Optional[str] = None
    scan_name: str
    captured_at: Optional[datetime] = None
    captured_by: Optional[str] = None


class ScanResponse(BaseModel):
    id: str
    scan_name: str
    facility_id: str
    node_id: Optional[str] = None
    file_format: ScanFileFormat
    file_size: int
    captured_at: Optional[datetime] = None
    captured_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ScanListParams(BaseModel):
    facility_id: Optional[str] = None
    node_id: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20


class ScanFileQuery(BaseModel):
    format: Optional[ScanFileFormat] = None
