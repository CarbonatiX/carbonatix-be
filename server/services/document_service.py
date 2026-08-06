from ..models import create_document
from ..schemas import DocumentBrief, DocumentsResponse


def upload_documents(db, company_id: str, files: list) -> DocumentsResponse:
    docs = []
    candidates = []
    for f in files:
        doc = create_document(
            db,
            company_id,
            file_id=f.filename,
            content_type=f.content_type or "application/octet-stream",
        )
        docs.append(DocumentBrief(document_id=doc["id"], status="processed"))
        # Placeholder: no real extraction yet
    return DocumentsResponse(documents=docs, candidates=candidates)
