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
    role: str = "admin"


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


# ── Documents (solo FE extraction shape) ──────────────────────────────


class DocumentBrief(BaseModel):
    document_id: str
    status: str


class CandidateResponse(BaseModel):
    """One OCR/interpret candidate for user review (never auto-accepted)."""

    field: str
    value: float | None
    confidence: float
    node: str
    sourceHint: str = ""
    basis: str | None = None
    evidence: str = ""
    derivation: str = ""


class DocumentExtractionResponse(BaseModel):
    candidates: list[CandidateResponse]
    confidenceIsPlaceholder: bool = True


# Legacy multi-upload shape kept for older clients (unused by FE slice-2).
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
# Nickel shape: RFC-006-Nickel-Forecasting-FINAL-v2.md §5.
# Carbon shape: RFC-006-price-forecasting(carbon-only).md §3.2 — field-for-field
# identical to carbonatix-ml/forecasting/contract.py's dataclasses.


class Staleness(BaseModel):
    is_stale: bool
    as_of: str | None = None
    age_hours: float | None = None


class NickelPointProvenance(BaseModel):
    bucket: str
    model_id: str
    cache_status: str


class NickelPoint(BaseModel):
    date: str
    price_usd_per_ton: float
    lower_usd_per_ton: float
    upper_usd_per_ton: float
    provenance: NickelPointProvenance


class NickelSummary(BaseModel):
    mean_usd_per_ton: float
    horizon_end_usd_per_ton: float
    trend: str
    trend_confidence: float
    change_pct: float


class NickelHistory(BaseModel):
    window: tuple[str, str]
    last_observed_price_usd_per_ton: float
    last_observed_date: str


class NickelBucketModel(BaseModel):
    bucket: str
    model_class: str
    trained_at: str


class NickelModelMeta(BaseModel):
    bucket_models: list[NickelBucketModel]
    dataset_version: str
    feature_set_version: str
    ruleset_version: str


class NickelForecast(BaseModel):
    series_id: str
    available: bool
    reason: str | None = None
    currency_unit: str
    interval_level: float
    points: list[NickelPoint] = Field(default_factory=list)
    summary: NickelSummary | None = None
    history: NickelHistory | None = None
    model: NickelModelMeta | None = None
    staleness: Staleness
    disclosures: list[str] = Field(default_factory=list)


class CarbonPoint(BaseModel):
    date: str
    price_idr_per_ton: float
    lower_idr_per_ton: float
    upper_idr_per_ton: float


class CarbonSummary(BaseModel):
    mean_idr_per_ton: float
    horizon_end_idr_per_ton: float
    last_observed_month: str
    last_observed_vwap_idr_per_ton: float
    trend: str
    trend_confidence: float
    change_pct: float


class CarbonMonthlyAnchor(BaseModel):
    month: str
    vwap_idr_per_ton: float
    volume_tco2e: float
    value_idr: float
    transaction_count: int


class CarbonMarketDepth(BaseModel):
    window: tuple[str, str]
    median_monthly_volume_tco2e: float
    max_monthly_volume_tco2e: float
    trailing_12m_volume_tco2e: float


class CarbonModelMeta(BaseModel):
    model_id: str
    model_class: str
    prophet_version: str
    trained_at: str
    training_data: str
    generator_seed: int
    generator_series_sha256: str
    artefact_sha256: str
    band_source: str
    band_sigma_monthly_log: float


class CarbonForecast(BaseModel):
    series_id: str
    available: bool
    reason: str | None = None
    currency_unit: str
    interval_level: float
    points: list[CarbonPoint] = Field(default_factory=list)
    summary: CarbonSummary | None = None
    monthly_anchors: list[CarbonMonthlyAnchor] = Field(default_factory=list)
    market_depth: CarbonMarketDepth | None = None
    model: CarbonModelMeta | None = None
    staleness: Staleness
    disclosures: list[str] = Field(default_factory=list)


class ForecastsResponse(BaseModel):
    generated_at: str
    horizon_days: int
    nickel: NickelForecast
    carbon: CarbonForecast


# ── Error ─────────────────────────────────────────────────────────────


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
