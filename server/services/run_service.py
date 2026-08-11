from emissions.calculator import calculate_emissions as _calculate_raw
from emissions.compliance import DEFAULT_CARBON_PRICE_IDR, assess
from fastapi import HTTPException
from models import create_run, find_company_by_id, find_run_by_id
from schemas import (
    Compliance,
    EmissionResult,
    ForecastSnapshot,
    RunDetail,
    RunRequest,
    RunResponse,
)
from services.emission_service import constants_from_site_spec
from services.forecast_service import get_forecasts
from services.twin_service import get_gaps


def _to_api_emission_result(raw) -> dict:
    intensity = raw.intensity_per_tonne_ni
    return EmissionResult(
        nickel_output_tons=round(raw.nickel_output_tons, 4),
        alloy_output_tons=round(raw.alloy_output_tons, 4),
        dryer_emissions=round(raw.dryer_emissions, 4),
        kiln_heat_emissions=round(raw.kiln_heat_emissions, 4),
        kiln_reductant_emissions=round(raw.kiln_reductant_emissions, 4),
        eaf_emissions=round(raw.eaf_emissions, 4),
        scope_1=round(raw.scope_1, 4),
        scope_2=round(raw.scope_2, 4),
        total_emissions=round(raw.total_emissions, 4),
        intensity_per_tonne_ni=(round(intensity, 4) if intensity is not None else None),
        dry_ore_tons=round(raw.dry_ore_tons, 4),
        dryer_coal_tons=round(raw.dryer_coal_tons, 4),
        kiln_coal_tons=round(raw.kiln_coal_tons, 4),
        reductant_tons=round(raw.reductant_tons, 4),
        eaf_mwh=round(raw.eaf_mwh, 4),
    ).model_dump()


def commit_run(db, company_id: str, user_id: str, req: RunRequest) -> RunResponse:
    gaps = get_gaps(db, company_id)
    if gaps.unbound_required_process_types or gaps.orphan_fields or gaps.ambiguous_fields:
        raise HTTPException(status_code=422, detail=gaps.model_dump())

    company = find_company_by_id(db, company_id)
    if not company:
        raise ValueError("Company not found")

    site_spec = company.get("site_spec") or {}
    constants = constants_from_site_spec(site_spec)
    snap = req.input_snapshot
    raw = _calculate_raw(
        wet_ore_input_tons=snap.wet_ore_input_tons,
        moisture_content_pct=snap.moisture_content_pct,
        nickel_grade_pct=snap.nickel_grade_pct,
        reductant_biocoke_pct=snap.reductant_biocoke_pct,
        sec_eaf_kwh_per_t_alloy=snap.sec_eaf_kwh_per_t_alloy,
        power_mix_captive_coal=snap.power_mix_captive_coal,
        ef_captive_pltu=snap.ef_captive_pltu,
        dryer_thermal_efficiency=snap.dryer_thermal_efficiency,
        constants=constants,
    )
    emission_result = _to_api_emission_result(raw)

    period_cap = company["period_cap_tco2e"]
    position = assess(
        raw,
        cap_tco2e=period_cap,
        carbon_price_idr_per_ton=DEFAULT_CARBON_PRICE_IDR,
    )
    # Indah API: position_tco2e positive = surplus (cap - projected).
    api_position = period_cap - position.projected_tco2e
    compliance = Compliance(
        period_cap_tco2e=period_cap,
        status="surplus" if position.is_compliant else "deficit",
        position_tco2e=api_position,
        value_idr=position.position_value_idr,
    )

    forecasts = get_forecasts(db, horizon_days=14)
    nickel_price = (
        forecasts.nickel.points[0].value
        if forecasts.nickel.available and forecasts.nickel.points
        else 0.0
    )
    carbon_price = (
        forecasts.carbon.points[0].value
        if forecasts.carbon.available and forecasts.carbon.points
        else 0.0
    )
    forecast_snapshot = ForecastSnapshot(
        nickel={"price_usd_per_ton": nickel_price},
        carbon={"limit_price_idr": carbon_price},
    )

    run = create_run(
        db,
        company_id=company_id,
        input_snapshot=req.input_snapshot.model_dump(),
        emission_result=emission_result,
        compliance=compliance.model_dump(),
        forecast_snapshot=forecast_snapshot.model_dump(),
        created_by_user_id=user_id,
    )

    return RunResponse(
        run=RunDetail(
            id=run["id"],
            input_snapshot=run["input_snapshot"],
            emission_result=run["emission_result"],
            compliance=Compliance(**run["compliance"]),
            forecast_snapshot=ForecastSnapshot(**run["forecast_snapshot"]),
            created_at=run["created_at"],
        )
    )


def get_run(db, company_id: str, run_id: str) -> RunResponse:
    run = find_run_by_id(db, run_id, company_id)
    if not run:
        raise ValueError("Run not found")
    return RunResponse(
        run=RunDetail(
            id=run["id"],
            input_snapshot=run["input_snapshot"],
            emission_result=run["emission_result"],
            compliance=Compliance(**run["compliance"]),
            forecast_snapshot=ForecastSnapshot(**run["forecast_snapshot"]),
            created_at=run["created_at"],
        )
    )
