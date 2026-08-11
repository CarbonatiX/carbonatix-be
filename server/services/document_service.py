"""Document upload + Helpy/Elice extraction. Candidates only — never auto-accept."""

from __future__ import annotations

import mimetypes

from ai_env import ensure_ai_env, require_ingestion_config
from fastapi import HTTPException, UploadFile, status
from ingestion.document_vision import ExtractionFailed, parse as parse_document
from ingestion.interpret import interpret as interpret_fields
from ingestion.mapping import readings_to_candidates
from models import create_document
from schemas import CandidateResponse, DocumentExtractionResponse

_MAX_UPLOAD_BYTES = 20 * 1024 * 1024
_SUPPORTED_MEDIA_TYPES = frozenset(
    {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/webp",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
)


def _resolve_upload_media_type(content_type: str | None, filename: str) -> str:
    if content_type and content_type in _SUPPORTED_MEDIA_TYPES:
        return content_type
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or (content_type or "application/octet-stream")


async def extract_document(
    db,
    company_id: str,
    file: UploadFile,
    profile: str,
) -> DocumentExtractionResponse:
    if profile not in ("site_spec", "operational"):
        raise HTTPException(status_code=422, detail="Unknown document profile")

    ensure_ai_env()
    try:
        require_ingestion_config()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    filename = file.filename or "document"
    media_type = _resolve_upload_media_type(file.content_type, filename)
    if media_type not in _SUPPORTED_MEDIA_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Could not read the document. Enter the values manually.",
        )

    file_bytes = await file.read(_MAX_UPLOAD_BYTES + 1)
    if len(file_bytes) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Dokumen terlalu besar. Maksimum 20 MB.",
        )

    # Persist metadata only; extraction result is returned for user review.
    create_document(
        db,
        company_id,
        file_id=filename,
        content_type=media_type,
    )

    try:
        parsed = await parse_document(file_bytes, media_type, filename)
        readings = await interpret_fields(parsed, profile)
        candidates = readings_to_candidates(readings, parsed)
    except ExtractionFailed as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not read the document. Enter the values manually.",
        ) from exc

    return DocumentExtractionResponse(
        candidates=[
            CandidateResponse(
                field=c.field,
                value=c.value,
                confidence=c.confidence,
                node=c.node,
                sourceHint=c.source_hint,
                basis=c.basis,
                evidence=c.evidence,
                derivation=c.derivation,
            )
            for c in candidates
        ],
        confidenceIsPlaceholder=True,
    )
