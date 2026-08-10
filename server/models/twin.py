from datetime import datetime, timezone

from bson import ObjectId


def _serialize(doc: dict) -> dict:
    doc["id"] = doc.pop("_id")
    return doc


def create_twin_model(db, company_id: str, file_id: str, parts: list[dict]) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "_id": f"twin_{ObjectId()}",
        "company_id": company_id,
        "file_id": file_id,
        "nodes": [],
        "created_at": now,
        "updated_at": now,
    }
    db.twin_models.insert_one(doc)
    return _serialize(doc)


def find_twin_by_company(db, company_id: str) -> dict | None:
    doc = db.twin_models.find_one({"company_id": company_id})
    return _serialize(doc) if doc else None


def upsert_twin_nodes(db, company_id: str, nodes: list[dict]) -> dict | None:
    now = datetime.now(timezone.utc).isoformat()
    db.twin_models.update_one(
        {"company_id": company_id},
        {"$set": {"nodes": nodes, "updated_at": now}},
        upsert=True,
    )
    return find_twin_by_company(db, company_id)


def add_twin_node(db, company_id: str, node: dict) -> dict | None:
    now = datetime.now(timezone.utc).isoformat()
    db.twin_models.update_one(
        {"company_id": company_id},
        {"$push": {"nodes": node}, "$set": {"updated_at": now}},
    )
    return find_twin_by_company(db, company_id)


def remove_twin_node(db, company_id: str, node_id: str) -> dict | None:
    now = datetime.now(timezone.utc).isoformat()
    db.twin_models.update_one(
        {"company_id": company_id},
        {"$pull": {"nodes": {"node_id": node_id}}, "$set": {"updated_at": now}},
    )
    return find_twin_by_company(db, company_id)
