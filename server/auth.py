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
    if user and check_password(password, user["password"]):
        token = create_token(user["username"], user.get("role", "viewer"))
        return {
            "username": user["username"],
            "name": user["name"],
            "role": user.get("role", "viewer"),
            "token": token,
        }
    return None


def register(db, username: str, name: str, password: str, role: str = "viewer") -> tuple[bool, str]:
    users = db["users"]
    if users.find_one({"username": username}):
        return False, "Username sudah ada!"

    users.insert_one({
        "username": username,
        "name": name,
        "password": hash_password(password),
        "role": role,
    })
    return True, "Register berhasil!"


def get_all_users(db) -> list:
    users = db["users"]
    return list(users.find({}, {"_id": 0, "password": 0}))


def delete_user(db, username: str) -> bool:
    users = db["users"]
    users.delete_one({"username": username})
    return True
