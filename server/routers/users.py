from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import get_db, get_current_user
from ..auth import hash_password
from ..models.user import (
    UserCreate, UserUpdate, UserApproval, UserResponse,
    UserListParams, UserRole, UserStatus
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def require_superadmin(user: dict = Depends(get_current_user)):
    if user.get("role") != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(req: UserCreate, db=Depends(get_db), user: dict = Depends(get_current_user)):
    users = db["users"]

    if users.find_one({"username": req.username}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    if users.find_one({"email": req.email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    now = datetime.now(timezone.utc)
    user_doc = {
        "username": req.username,
        "email": req.email,
        "password": hash_password(req.password),
        "full_name": req.full_name,
        "role": req.role.value,
        "facility_id": req.facility_id,
        "phone_number": req.phone_number,
        "status": UserStatus.pending.value,
        "is_active": False,
        "created_at": now,
        "updated_at": now,
    }

    result = users.insert_one(user_doc)
    user_doc["id"] = str(result.inserted_id)
    del user_doc["password"]

    return user_doc


@router.get("/", response_model=dict)
def list_users(
    role: UserRole = None,
    facility_id: str = None,
    status: UserStatus = None,
    search: str = None,
    page: int = 1,
    page_size: int = 20,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    users = db["users"]
    query = {}

    if role:
        query["role"] = role.value
    if facility_id:
        query["facility_id"] = facility_id
    if status:
        query["status"] = status.value
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"username": {"$regex": search, "$options": "i"}},
        ]

    skip = (page - 1) * page_size
    total = users.count_documents(query)
    cursor = users.find(query, {"password": 0}).skip(skip).limit(page_size)

    items = []
    for u in cursor:
        u["id"] = str(u["_id"])
        del u["_id"]
        items.append(u)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    req: UserUpdate,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    users = db["users"]

    from bson import ObjectId
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    existing = users.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = req.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    if "role" in update_data:
        update_data["role"] = update_data["role"].value

    update_data["updated_at"] = datetime.now(timezone.utc)

    users.update_one({"_id": obj_id}, {"$set": update_data})

    updated = users.find_one({"_id": obj_id}, {"password": 0})
    updated["id"] = str(updated["_id"])
    del updated["_id"]

    return updated


@router.put("/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: str,
    req: UserApproval,
    db=Depends(get_db),
    user: dict = Depends(require_superadmin)
):
    users = db["users"]

    from bson import ObjectId
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    existing = users.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = {
        "status": req.status.value,
        "approved_by": req.approved_by,
        "approved_at": req.approved_at,
        "is_active": req.status == UserStatus.approved,
        "updated_at": datetime.now(timezone.utc),
    }

    users.update_one({"_id": obj_id}, {"$set": update_data})

    updated = users.find_one({"_id": obj_id}, {"password": 0})
    updated["id"] = str(updated["_id"])
    del updated["_id"]

    return updated
