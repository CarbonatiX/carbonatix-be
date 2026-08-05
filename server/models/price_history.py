def get_price_history(db, commodity: str) -> list[dict]:
    return list(db.price_history.find({"commodity": commodity}))


def upsert_price_history(db, commodity: str, points: list[dict]) -> None:
    db.price_history.delete_many({"commodity": commodity})
    for p in points:
        p["commodity"] = commodity
    db.price_history.insert_many(points)
