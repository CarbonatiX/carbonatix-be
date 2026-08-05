from datetime import datetime, timezone


def get_latest_forecast(db) -> dict | None:
    return db.forecasts.find_one(sort=[("updated_at", -1)])


def upsert_forecast(db, data: dict) -> None:
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    db.forecasts.delete_many({})
    db.forecasts.insert_one(data)
