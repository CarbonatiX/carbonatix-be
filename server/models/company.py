from datetime import datetime, timezone
from bson import ObjectId


def _serialize(doc: dict) -> dict:
    doc["id"] = doc.pop("_id")
    return doc


def create_company(db, owner_user_id: str, name: str, technology: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": f"cmp_{ObjectId()}",
        "owner_user_id": owner_user_id,
        "name": name,
        "technology": technology,
        "period_cap_tco2e": 0.0,
        "site_spec": {
            "ef_captive_pltu": 0.0,
            "dryer_thermal_efficiency": 0.0,
            "sec_eaf_kwh_per_t_alloy": 0.0,
            "alloy_nickel_grade": 0.0,
            "kiln_thermal_efficiency": 0.0,
        },
        "constant_overrides": {},
        "created_at": now,
        "updated_at": now,
    }
    db.companies.insert_one(doc)
    return _serialize(doc)


def find_company_by_id(db, company_id: str) -> dict | None:
    doc = db.companies.find_one({"_id": company_id})
    return _serialize(doc) if doc else None


def update_company(db, company_id: str, updates: dict) -> dict | None:
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    db.companies.update_one({"_id": company_id}, {"$set": updates})
    return find_company_by_id(db, company_id)
