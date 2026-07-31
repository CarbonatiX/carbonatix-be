import bcrypt
import jwt
import datetime
from .config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(username: str, role: str) -> str:
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login(db, username: str, password: str) -> dict | None:
    users = db["users"]
    user = users.find_one({"username": username})
    if not user:
        return None
    if not check_password(password, user["password"]):
        return None
    if user.get("status") != "approved":
        return {"error": "Akun belum disetujui. Hubungi admin."}
    if not user.get("is_active", True):
        return {"error": "Akun tidak aktif."}
    token = create_token(user["username"], user.get("role", "viewer"))
    return {
        "username": user["username"],
        "name": user["name"],
        "role": user.get("role", "viewer"),
        "token": token,
    }


def register(db, username: str, name: str, password: str, email: str = "", facility_id: str = "") -> tuple[bool, str]:
    users = db["users"]
    if users.find_one({"username": username}):
        return False, "Username sudah ada!"
    if email and users.find_one({"email": email}):
        return False, "Email sudah terdaftar!"

    now = datetime.datetime.now(datetime.timezone.utc)
    users.insert_one({
        "username": username,
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": "viewer",
        "facility_id": facility_id,
        "is_active": True,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    })
    return True, "Register berhasil! Menunggu persetujuan admin."


def get_all_users(db) -> list:
    users = db["users"]
    return list(users.find({}, {"_id": 0, "password": 0}))


def get_pending_users(db) -> list:
    users = db["users"]
    return list(users.find({"status": "pending"}, {"_id": 1, "username": 1, "name": 1, "email": 1, "facility_id": 1, "created_at": 1}))


def approve_user(db, user_id: str, approved: bool) -> tuple[bool, str]:
    users = db["users"]
    from bson import ObjectId
    new_status = "approved" if approved else "rejected"
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": new_status, "updated_at": datetime.datetime.now(datetime.timezone.utc)}}
    )
    if result.modified_count:
        return True, f"User {'disetujui' if approved else 'ditolak'}"
    return False, "User tidak ditemukan"


def delete_user(db, username: str) -> bool:
    users = db["users"]
    users.delete_one({"username": username})
    return True
