"""Seed data for CarbonatiX ERP"""
from .auth import hash_password
from datetime import datetime


SEED_USERS = [
    {
        "username": "admin",
        "name": "Administrator",
        "email": "admin@carbonatix.com",
        "password": hash_password("admin123"),
        "role": "superadmin",
        "facility_id": "FAC001",
        "phone_number": "081234567890",
        "is_active": True,
        "status": "approved",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "username": "operator1",
        "name": "Operator Utama",
        "email": "operator1@carbonatix.com",
        "password": hash_password("operator123"),
        "role": "operator",
        "facility_id": "FAC001",
        "phone_number": "081234567891",
        "is_active": True,
        "status": "approved",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "username": "viewer1",
        "name": "Viewer Plant",
        "email": "viewer1@carbonatix.com",
        "password": hash_password("viewer123"),
        "role": "viewer",
        "facility_id": "FAC001",
        "is_active": True,
        "status": "approved",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

SEED_NODES = [
    {
        "node_id": "NODE001",
        "node_name": "Furnace Line 4",
        "facility_id": "FAC001",
        "line": "RKEF Line 4",
        "latitude": -2.5,
        "longitude": 115.5,
        "node_type": "furnace",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "node_id": "NODE002",
        "node_name": "Converter Line 4",
        "facility_id": "FAC001",
        "line": "RKEF Line 4",
        "latitude": -2.501,
        "longitude": 115.501,
        "node_type": "converter",
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]


def seed_database(db):
    """Seed the database with initial data if empty"""
    users = db["users"]
    nodes = db["nodes"]

    # Seed users only if empty
    if users.count_documents({}) == 0:
        users.insert_many(SEED_USERS)
        print(f"Seeded {len(SEED_USERS)} users")
    else:
        print("Users collection not empty, skipping seed")

    # Seed nodes only if empty
    if nodes.count_documents({}) == 0:
        nodes.insert_many(SEED_NODES)
        print(f"Seeded {len(SEED_NODES)} nodes")
    else:
        print("Nodes collection not empty, skipping seed")


if __name__ == "__main__":
    from .database import get_database
    db = get_database()
    if db:
        seed_database(db)
        print("Seed completed!")
    else:
        print("Failed to connect to database")
