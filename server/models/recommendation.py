from datetime import datetime, timezone
from bson import ObjectId


def _serialize(doc: dict) -> dict:
    doc["id"] = doc.pop("_id")
    return doc


def create_recommendation(
    db,
    company_id: str,
    run_id: str,
    trace: list[dict],
    text: str,
    citations: list[dict],
    confidence: float,
    model_id: str,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": f"rec_{ObjectId()}",
        "company_id": company_id,
        "run_id": run_id,
        "trace": trace,
        "text": text,
        "citations": citations,
        "confidence": confidence,
        "model_id": model_id,
        "created_at": now,
    }
    db.recommendations.insert_one(doc)
    return _serialize(doc)


def find_recommendation_by_run(db, run_id: str, company_id: str) -> dict | None:
    doc = db.recommendations.find_one({"run_id": run_id, "company_id": company_id})
    return _serialize(doc) if doc else None
