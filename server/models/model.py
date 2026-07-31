from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ModelType(str, Enum):
    emission_prediction = "emission_prediction"
    what_if_simulation = "what_if_simulation"


class ModelStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    training = "training"
    failed = "failed"


class ModelResponse(BaseModel):
    id: str
    model_name: str
    model_type: ModelType
    facility_id: str
    status: ModelStatus
    version: str
    accuracy: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class ModelListParams(BaseModel):
    facility_id: Optional[str] = None
    model_type: Optional[ModelType] = None
    status: Optional[ModelStatus] = None
    page: int = 1
    page_size: int = 20


class SimulationRequest(BaseModel):
    facility_id: str
    shift_coal_to_hydro_pct: int
    production_capacity_overdrive_pct: int
    ore_quality_moisture_ni_grade_pct: int
    inject_bio_coke_reductant: bool


class SimulationResult(BaseModel):
    id: str
    facility_id: str
    simulation_request: Dict[str, Any]
    predicted_emissions: float
    predicted_intensity: float
    confidence_score: float
    recommendations: Optional[Dict[str, Any]] = None
    created_at: datetime
