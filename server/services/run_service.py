from models import create_run, find_company_by_id, find_run_by_id
from schemas import Compliance, ForecastSnapshot, RunDetail, RunRequest, RunResponse
from services.emission_service import calculate_emissions
from services.forecast_service import get_forecasts


def commit_run(db, company_id: str, user_id: str, req: RunRequest) -> RunResponse:
    emission_resp = calculate_emissions(req.input_snapshot)
    emission_result = emission_resp.emission_result.model_dump()

    company = find_company_by_id(db, company_id)
    if not company:
        raise ValueError("Company not found")

    period_cap = company["period_cap_tco2e"]
    total = emission_result["total_emissions"]
    position = period_cap - total
    status = "surplus" if position >= 0 else "deficit"
    value_idr = abs(position) * 35200

    compliance = Compliance(
        period_cap_tco2e=period_cap,
        status=status,
        position_tco2e=position,
        value_idr=value_idr,
    )

    forecasts = get_forecasts(db, horizon_days=14)
    forecast_snapshot = ForecastSnapshot(
        nickel={
            "price_usd_per_ton": (
                forecasts.nickel_forecast.points[0].price_usd_per_ton
                if forecasts.nickel_forecast.points
                else 0
            )
        },
        carbon={
            "limit_price_idr": (
                forecasts.carbon_forecast.points[0].limit_price_idr
                if forecasts.carbon_forecast.points
                else 0
            )
        },
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
