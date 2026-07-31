from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class NodeType(str, Enum):
    furnace = "furnace"
    converter = "converter"
    casting = "casting"


class NodeStatus(str, Enum):
    active = "active"
    idle = "idle"
    maintenance = "maintenance"


class Granularity(str, Enum):
    raw = "raw"
    hourly = "hourly"
    daily = "daily"


class NodeCreate(BaseModel):
    node_id: str
    node_name: str
    facility_id: str
    line: str
    latitude: float
    longitude: float
    node_type: NodeType
    status: NodeStatus


class NodeUpdate(BaseModel):
    node_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[NodeStatus] = None
    node_type: Optional[NodeType] = None


class NodeParameterInput(BaseModel):
    timestamp: datetime
    electrode_load: Optional[float] = None
    tap_temperature: Optional[float] = None
    power_draw: Optional[float] = None
    hourly_emissions: Optional[float] = None
    ptbae_pu_cap_contribution: Optional[float] = None
    ore_input_vol: Optional[float] = None
    avg_moisture: Optional[float] = None
    nickel_grade: Optional[float] = None
    total_power_draw: Optional[float] = None
    scope_process: Optional[float] = None
    scope_grid: Optional[float] = None
    current_intensity: Optional[float] = None


class NodeParameterResponse(BaseModel):
    id: str
    node_id: str
    timestamp: datetime
    electrode_load: Optional[float] = None
    tap_temperature: Optional[float] = None
    power_draw: Optional[float] = None
    hourly_emissions: Optional[float] = None
    ptbae_pu_cap_contribution: Optional[float] = None
    ore_input_vol: Optional[float] = None
    avg_moisture: Optional[float] = None
    nickel_grade: Optional[float] = None
    total_power_draw: Optional[float] = None
    scope_process: Optional[float] = None
    scope_grid: Optional[float] = None
    current_intensity: Optional[float] = None
    created_at: datetime


class NodeResponse(BaseModel):
    id: str
    node_id: str
    node_name: str
    facility_id: str
    line: str
    latitude: float
    longitude: float
    node_type: NodeType
    status: NodeStatus
    created_at: datetime
    updated_at: datetime


class NodeListParams(BaseModel):
    facility_id: Optional[str] = None
    status: Optional[NodeStatus] = None
    node_type: Optional[NodeType] = None
    page: int = 1
    page_size: int = 20


class NodeParameterQuery(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    granularity: Optional[Granularity] = None
