from datetime import datetime, timezone

from bson import ObjectId


def _serialize(doc: dict) -> dict:
    doc["id"] = doc.pop("_id")
    return doc


def create_document(db, company_id: str, file_id: str, content_type: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": f"doc_{ObjectId()}",
        "company_id": company_id,
        "file_id": file_id,
        "content_type": content_type,
        "extraction": {"status": "pending", "raw_result": {}, "candidates": []},
        "created_at": now,
    }
    db.documents.insert_one(doc)
    return _serialize(doc)


def find_document_by_id(db, doc_id: str, company_id: str) -> dict | None:
    doc = db.documents.find_one({"_id": doc_id, "company_id": company_id})
    return _serialize(doc) if doc else None


def list_documents_by_company(db, company_id: str) -> list[dict]:
    return [_serialize(d) for d in db.documents.find({"company_id": company_id})]
