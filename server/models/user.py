from datetime import datetime, timezone

from bson import ObjectId


def _serialize(doc: dict) -> dict:
    doc["id"] = doc.pop("_id")
    return doc


def create_user(
    db, email: str, password_hash: str, company_id: str, role: str = "admin"
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": f"usr_{ObjectId()}",
        "email": email,
        "password_hash": password_hash,
        "company_id": company_id,
        "role": role,
        "created_at": now,
        "updated_at": now,
    }
    db.users.insert_one(doc)
    return _serialize(doc)


def find_user_by_email(db, email: str) -> dict | None:
    doc = db.users.find_one({"email": email})
    return _serialize(doc) if doc else None


def find_user_by_id(db, user_id: str) -> dict | None:
    doc = db.users.find_one({"_id": user_id})
    return _serialize(doc) if doc else None
