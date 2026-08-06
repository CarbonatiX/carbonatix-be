from pydantic import BaseModel, EmailStr, Field

# ── Auth ──────────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserBrief(BaseModel):
    id: str
    email: str


class AuthResponse(BaseModel):
    user: UserBrief
    token: str


# ── Company ───────────────────────────────────────────────────────────


class SiteSpec(BaseModel):
    ef_captive_pltu: float
    dryer_thermal_efficiency: float
    sec_eaf_kwh_per_t_alloy: float
    alloy_nickel_grade: float
    kiln_thermal_efficiency: float


class CompanyDetail(BaseModel):
    id: str
    name: str
    technology: str
    period_cap_tco2e: float
    site_spec: SiteSpec


class CompanyResponse(BaseModel):
    company: CompanyDetail


class CompanyUpdate(BaseModel):
    name: str | None = None
    technology: str | None = None
    period_cap_tco2e: float | None = None
    site_spec: SiteSpec | None = None


# ── Twin ──────────────────────────────────────────────────────────────


class TwinPart(BaseModel):
    mesh_ref: str
    label: str


class TwinModelInner(BaseModel):
    id: str
    file_id: str
    parts: list[TwinPart]


class TwinModelResponse(BaseModel):
    twin_model: TwinModelInner


class TwinNode(BaseModel):
    node_id: str
    label: str
    mesh_ref: str
    process_type: str


class TwinNodesResponse(BaseModel):
    twin_model_id: str
    nodes: list[TwinNode]


class TwinNodesUpdate(BaseModel):
    nodes: list[TwinNode]


class OrphanField(BaseModel):
    field_name: str
    owning_process_type: str
    document_id: str


class AmbiguousField(BaseModel):
    field_name: str
    owning_process_type: str
    candidate_node_ids: list[str]


class TwinGapsResponse(BaseModel):
    unbound_required_process_types: list[str]
    orphan_fields: list[OrphanField]
    ambiguous_fields: list[AmbiguousField]


# ── Documents ─────────────────────────────────────────────────────────


class DocumentBrief(BaseModel):
    document_id: str
    status: str


class DocumentCandidate(BaseModel):
    candidate_id: str
    field_name: str
    value: float
    confidence: float
    owning_process_type: str
    routing_status: str
    target_node_id: str
    accepted: bool


class DocumentsResponse(BaseModel):
    documents: list[DocumentBrief]
    candidates: list[DocumentCandidate]


# ── Emissions ─────────────────────────────────────────────────────────


class EmissionRequest(BaseModel):
    wet_ore_input_tons: float
    moisture_content_pct: float = Field(ge=0, le=1)
    nickel_grade_pct: float = Field(ge=0, le=1)
    reductant_biocoke_pct: float = Field(ge=0, le=1)
    sec_eaf_kwh_per_t_alloy: float
    power_mix_captive_coal: float = Field(ge=0, le=1)
    power_mix_hydro_grid: float = Field(ge=0, le=1)
    ef_captive_pltu: float
    dryer_thermal_efficiency: float


class EmissionResult(BaseModel):
    nickel_output_tons: float
    alloy_output_tons: float
    dryer_emissions: float
    kiln_heat_emissions: float
    kiln_reductant_emissions: float
    eaf_emissions: float
    scope_1: float
    scope_2: float
    total_emissions: float
    intensity_per_tonne_ni: float | None
    dry_ore_tons: float
    dryer_coal_tons: float
    kiln_coal_tons: float
    reductant_tons: float
    eaf_mwh: float


class EmissionResponse(BaseModel):
    emission_result: EmissionResult


# ── Runs ──────────────────────────────────────────────────────────────


class RunRequest(BaseModel):
    input_snapshot: EmissionRequest


class Compliance(BaseModel):
    period_cap_tco2e: float
    status: str
    position_tco2e: float
    value_idr: float


class ForecastSnapshot(BaseModel):
    nickel: dict
    carbon: dict


class RunDetail(BaseModel):
    id: str
    input_snapshot: dict
    emission_result: dict
    compliance: Compliance
    forecast_snapshot: ForecastSnapshot
    created_at: str


class RunResponse(BaseModel):
    run: RunDetail


# ── Forecasts ─────────────────────────────────────────────────────────


class NickelPoint(BaseModel):
    date: str
    price_usd_per_ton: float
    lower_usd_per_ton: float
    upper_usd_per_ton: float


class CarbonPoint(BaseModel):
    date: str
    limit_price_idr: float
    lower_limit_price_idr: float
    upper_limit_price_idr: float


class NickelForecast(BaseModel):
    currency: str
    points: list[NickelPoint]
    stale: bool


class CarbonForecast(BaseModel):
    currency: str
    points: list[CarbonPoint]
    stale: bool


class ForecastsResponse(BaseModel):
    horizon_days: int
    nickel_forecast: NickelForecast
    carbon_forecast: CarbonForecast


# ── Error ─────────────────────────────────────────────────────────────


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
