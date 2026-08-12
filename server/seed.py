from auth import hash_password
from models import create_company, create_user
from services.bundled_twin import ensure_bundled_twin


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
