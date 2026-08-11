from datetime import datetime, timedelta, timezone

from models import get_latest_forecast
from schemas import (
    ForecastHistory,
    ForecastModelInfo,
    ForecastPoint,
    ForecastSeries,
    ForecastsResponse,
    ForecastStaleness,
    ForecastSummary,
)


def _summary_from_points(points: list[ForecastPoint]) -> ForecastSummary:
    values = [p.value for p in points]
    return ForecastSummary(
        start_value=values[0],
        end_value=values[-1],
        min_value=min(values),
        max_value=max(values),
        mean_value=sum(values) / len(values),
    )


def _build_series(
    *,
    series_id: str,
    currency_unit: str,
    points: list[ForecastPoint],
    model_name: str,
    disclosures: list[str],
    generated_at: str,
) -> ForecastSeries:
    return ForecastSeries(
        series_id=series_id,
        available=True,
        currency_unit=currency_unit,
        interval_level=0.8,
        points=points,
        summary=_summary_from_points(points),
        history=ForecastHistory(
            lookback_days=90,
            last_value=points[0].value if points else None,
            points=[],
        ),
        model=ForecastModelInfo(
            name=model_name,
            version="0.1.0",
            artefact_id=None,
            trained_at=None,
        ),
        staleness=ForecastStaleness(
            is_stale=False,
            as_of=generated_at,
            max_age_hours=24.0,
            age_hours=0.0,
        ),
        disclosures=disclosures,
    )


def get_forecasts(db, horizon_days: int = 14) -> ForecastsResponse:
    cached = get_latest_forecast(db)
    if cached:
        payload = {k: v for k, v in cached.items() if k != "_id" and k != "updated_at"}
        return ForecastsResponse(**payload)

    generated_at = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date()

    nickel_points: list[ForecastPoint] = []
    carbon_points: list[ForecastPoint] = []
    for i in range(horizon_days):
        d = (today + timedelta(days=i)).isoformat()
        nickel_points.append(
            ForecastPoint(
                date=d,
                value=15400.0,
                lower=14900.0,
                upper=15900.0,
            )
        )
        carbon_points.append(
            ForecastPoint(
                date=d,
                value=42000.0,
                lower=39000.0,
                upper=46000.0,
            )
        )

    return ForecastsResponse(
        generated_at=generated_at,
        horizon_days=horizon_days,
        nickel=_build_series(
            series_id="lme_nickel",
            currency_unit="usd_per_ton",
            points=nickel_points,
            model_name="nickel_stub",
            disclosures=[],
            generated_at=generated_at,
        ),
        carbon=_build_series(
            series_id="idx_carbon",
            currency_unit="idr_per_ton",
            points=carbon_points,
            model_name="carbon_stub",
            disclosures=[
                (
                    "Carbon path is a synthetic daily series anchored to "
                    "published IDX monthly aggregates."
                )
            ],
            generated_at=generated_at,
        ),
    )
