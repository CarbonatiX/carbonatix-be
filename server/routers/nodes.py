from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import get_db, get_current_user
from ..models.node import (
    NodeCreate, NodeUpdate, NodeResponse, NodeListParams,
    NodeParameterInput, NodeParameterResponse, NodeParameterQuery
)

router = APIRouter(prefix="/api/v1/nodes", tags=["nodes"])


@router.post("/", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(req: NodeCreate, db=Depends(get_db), user: dict = Depends(get_current_user)):
    nodes = db["nodes"]

    if nodes.find_one({"node_id": req.node_id}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Node ID already exists"
        )

    now = datetime.now(timezone.utc)
    node_doc = {
        "node_id": req.node_id,
        "node_name": req.node_name,
        "facility_id": req.facility_id,
        "line": req.line,
        "latitude": req.latitude,
        "longitude": req.longitude,
        "node_type": req.node_type.value,
        "status": req.status.value,
        "created_at": now,
        "updated_at": now,
    }

    result = nodes.insert_one(node_doc)
    node_doc["id"] = str(result.inserted_id)

    return node_doc


@router.get("/", response_model=dict)
def list_nodes(
    facility_id: str = None,
    node_type: str = None,
    node_status: str = None,
    page: int = 1,
    page_size: int = 20,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    nodes = db["nodes"]
    query = {}

    if facility_id:
        query["facility_id"] = facility_id
    if node_type:
        query["node_type"] = node_type
    if node_status:
        query["status"] = node_status

    skip = (page - 1) * page_size
    total = nodes.count_documents(query)
    cursor = nodes.find(query).skip(skip).limit(page_size)

    items = []
    for n in cursor:
        n["id"] = str(n["_id"])
        del n["_id"]
        items.append(n)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: str,
    req: NodeUpdate,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    nodes = db["nodes"]

    existing = nodes.find_one({"node_id": node_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    update_data = req.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    if "node_type" in update_data:
        update_data["node_type"] = update_data["node_type"].value

    update_data["updated_at"] = datetime.now(timezone.utc)

    nodes.update_one({"node_id": node_id}, {"$set": update_data})

    updated = nodes.find_one({"node_id": node_id})
    updated["id"] = str(updated["_id"])
    del updated["_id"]

    return updated


@router.post("/{node_id}/parameters", response_model=NodeParameterResponse, status_code=status.HTTP_201_CREATED)
def add_node_parameters(
    node_id: str,
    req: NodeParameterInput,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    nodes = db["nodes"]
    node_params = db["node_parameters"]

    if not nodes.find_one({"node_id": node_id}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    now = datetime.now(timezone.utc)
    param_doc = {
        "node_id": node_id,
        "timestamp": req.timestamp,
        "electrode_load": req.electrode_load,
        "tap_temperature": req.tap_temperature,
        "power_draw": req.power_draw,
        "hourly_emissions": req.hourly_emissions,
        "ptbae_pu_cap_contribution": req.ptbae_pu_cap_contribution,
        "ore_input_vol": req.ore_input_vol,
        "avg_moisture": req.avg_moisture,
        "nickel_grade": req.nickel_grade,
        "total_power_draw": req.total_power_draw,
        "scope_process": req.scope_process,
        "scope_grid": req.scope_grid,
        "current_intensity": req.current_intensity,
        "created_at": now,
    }

    result = node_params.insert_one(param_doc)
    param_doc["id"] = str(result.inserted_id)

    return param_doc


@router.get("/{node_id}/parameters", response_model=dict)
def get_node_parameters(
    node_id: str,
    date_from: datetime = None,
    date_to: datetime = None,
    granularity: str = None,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    nodes = db["nodes"]
    node_params = db["node_parameters"]

    if not nodes.find_one({"node_id": node_id}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )

    query = {"node_id": node_id}

    if date_from:
        query["timestamp"] = {"$gte": date_from}
    if date_to:
        if "timestamp" not in query:
            query["timestamp"] = {}
        query["timestamp"]["$lte"] = date_to

    cursor = node_params.find(query).sort("timestamp", -1)

    items = []
    for p in cursor:
        p["id"] = str(p["_id"])
        del p["_id"]
        items.append(p)

    if granularity == "hourly":
        hourly = {}
        for item in items:
            key = item["timestamp"].strftime("%Y-%m-%d-%H")
            if key not in hourly:
                hourly[key] = item
        items = list(hourly.values())
    elif granularity == "daily":
        daily = {}
        for item in items:
            key = item["timestamp"].strftime("%Y-%m-%d")
            if key not in daily:
                daily[key] = item
        items = list(daily.values())

    return {
        "items": items,
        "total": len(items),
    }
