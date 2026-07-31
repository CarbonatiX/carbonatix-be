from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from ..deps import get_db, get_current_user
from ..models.model import (
    ModelType, ModelStatus, ModelResponse,
    SimulationRequest, SimulationResult
)

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("/", response_model=dict)
def list_models(
    facility_id: str = None,
    model_type: str = None,
    model_status: str = None,
    page: int = 1,
    page_size: int = 20,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    models = db["models"]
    query = {}

    if facility_id:
        query["facility_id"] = facility_id
    if model_type:
        query["model_type"] = model_type
    if model_status:
        query["status"] = model_status

    skip = (page - 1) * page_size
    total = models.count_documents(query)
    cursor = models.find(query).skip(skip).limit(page_size)

    items = []
    for m in cursor:
        m["id"] = str(m["_id"])
        del m["_id"]
        items.append(m)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.post("/simulate", response_model=dict, status_code=status.HTTP_201_CREATED)
def simulate(
    req: SimulationRequest,
    db=Depends(get_db),
    user: dict = Depends(get_current_user)
):
    facilities = db["facilities"]
    facility = facilities.find_one({"facility_id": req.facility_id})
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )

    baseline_emissions = facility.get("current_emissions", 0)

    coal_factor = 1 - (req.shift_coal_to_hydro_pct / 100) * 0.6
    overdrive_factor = req.production_capacity_overdrive_pct / 100
    moisture_factor = 1 + (req.ore_quality_moisture_ni_grade_pct - 50) / 200
    bio_coke_factor = 0.9 if req.inject_bio_coke_reductant else 1.0

    simulated_emissions = (
        baseline_emissions
        * coal_factor
        * overdrive_factor
        * moisture_factor
        * bio_coke_factor
    )

    reduction_pct = ((baseline_emissions - simulated_emissions) / baseline_emissions) * 100 if baseline_emissions else 0
    intensity_change = simulated_emissions - baseline_emissions

    recommendations = []
    if req.shift_coal_to_hydro_pct > 0:
        recommendations.append(
            f"Shifting {req.shift_coal_to_hydro_pct}% of coal to hydro could reduce emissions by ~{req.shift_coal_to_hydro_pct * 0.6:.1f}%."
        )
    if req.production_capacity_overdrive_pct > 100:
        recommendations.append(
            f"Running at {req.production_capacity_overdrive_pct}% capacity increases proportional emissions. Consider energy efficiency offsets."
        )
    if req.ore_quality_moisture_ni_grade_pct > 60:
        recommendations.append(
            "High moisture content increases energy demand. Pre-drying ore before smelting is recommended."
        )
    if req.inject_bio_coke_reductant:
        recommendations.append(
            "Bio-coke reductant substitution reduces carbon intensity. Verify supply chain sustainability certification."
        )

    now = datetime.now(timezone.utc)
    sim_doc = {
        "facility_id": req.facility_id,
        "simulation_request": req.model_dump(),
        "predicted_emissions": simulated_emissions,
        "predicted_intensity": intensity_change,
        "confidence_score": 0.85,
        "recommendations": {"list": recommendations},
        "created_at": now,
    }

    simulations = db["simulations"]
    result = simulations.insert_one(sim_doc)
    sim_doc["id"] = str(result.inserted_id)

    return {
        "facility_id": req.facility_id,
        "baseline_emissions": baseline_emissions,
        "simulated_emissions": simulated_emissions,
        "reduction_pct": reduction_pct,
        "intensity_change": intensity_change,
        "recommendations": recommendations,
    }
