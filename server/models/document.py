from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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
    uploaded_by: Optional[str] = None
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
    uploaded_by: Optional[str] = None
    tags: Optional[List[str]] = None
    extraction_status: Optional[ExtractionStatus] = None
    file_size: int
    created_at: datetime
    updated_at: datetime


class DocumentListParams(BaseModel):
    facility_id: Optional[str] = None
    document_type: Optional[DocumentType] = None
    status: Optional[ExtractionStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20
