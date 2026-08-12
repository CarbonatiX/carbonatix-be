import json
import os
from pathlib import Path

from auth import hash_password
from models import create_company, create_user, upsert_forecast
from services.bundled_twin import ensure_bundled_twin

_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "data" / "forecasts_mvp.json"


def seed_database(db):
    if db.users.count_documents({}) > 0:
        return

    pw_hash = hash_password("test123!")
    company = create_company(
        db, owner_user_id="", name="Demo Smelter", technology="RKEF"
    )
    company["period_cap_tco2e"] = 480000.0
    company["site_spec"] = {
        "ef_captive_pltu": 0.98,
        "dryer_thermal_efficiency": 0.82,
        "sec_eaf_kwh_per_t_alloy": 3200.0,
        "alloy_nickel_grade": 0.12,
        "kiln_thermal_efficiency": 0.74,
    }
    db.companies.update_one({"_id": company["id"]}, {"$set": company})

    user = create_user(db, "demo@carbonatix.com", pw_hash, company["id"], role="admin")
    db.companies.update_one(
        {"_id": company["id"]}, {"$set": {"owner_user_id": user["id"]}}
    )
    ensure_bundled_twin(db, company["id"])

    print("Seeded admin: demo@carbonatix.com / test123!")


def seed_forecasts(db) -> bool:
    """Load packaged ML forecast envelope into Mongo when empty (or forced).

    Returns True if an upsert ran.
    """
    if os.getenv("SKIP_FORECAST_SEED", "").strip() in {"1", "true", "True", "yes"}:
        return False
    force = os.getenv("FORCE_FORECAST_SEED", "").strip() in {"1", "true", "True", "yes"}
    if not force and db.forecasts.count_documents({}) > 0:
        return False
    if not _FIXTURE_PATH.exists():
        print(f"Forecast fixture missing: {_FIXTURE_PATH}")
        return False
    payload = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    upsert_forecast(db, payload)
    print(f"Seeded forecasts from {_FIXTURE_PATH.name}")
    return True
