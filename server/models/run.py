from datetime import datetime, timezone

from bson import ObjectId


def _serialize(doc: dict) -> dict:
    doc["id"] = doc.pop("_id")
    return doc


def create_run(
    db,
    company_id: str,
    input_snapshot: dict,
    emission_result: dict,
    compliance: dict,
    forecast_snapshot: dict,
    created_by_user_id: str,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": f"run_{ObjectId()}",
        "company_id": company_id,
        "input_snapshot": input_snapshot,
        "emission_result": emission_result,
        "compliance": compliance,
        "forecast_snapshot": forecast_snapshot,
        "created_by_user_id": created_by_user_id,
        "created_at": now,
    }
    db.calculation_runs.insert_one(doc)
    return _serialize(doc)


def find_run_by_id(db, run_id: str, company_id: str) -> dict | None:
    doc = db.calculation_runs.find_one({"_id": run_id, "company_id": company_id})
    return _serialize(doc) if doc else None
