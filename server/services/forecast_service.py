from datetime import datetime, timedelta, timezone

from models import get_latest_forecast
from schemas import (
    CarbonForecast,
    CarbonPoint,
    ForecastsResponse,
    NickelForecast,
    NickelPoint,
)


def get_forecasts(db, horizon_days: int = 14) -> ForecastsResponse:
    cached = get_latest_forecast(db)
    if cached:
        return ForecastsResponse(**cached)

    today = datetime.now(timezone.utc).date()
    nickel_points = []
    carbon_points = []
    for i in range(horizon_days):
        d = (today + timedelta(days=i)).isoformat()
        nickel_points.append(
            NickelPoint(
                date=d,
                price_usd_per_ton=15400.0,
                lower_usd_per_ton=14900.0,
                upper_usd_per_ton=15900.0,
            )
        )
        carbon_points.append(
            CarbonPoint(
                date=d,
                limit_price_idr=42000.0,
                lower_limit_price_idr=39000.0,
                upper_limit_price_idr=46000.0,
            )
        )

    return ForecastsResponse(
        horizon_days=horizon_days,
        nickel_forecast=NickelForecast(
            currency="USD", points=nickel_points, stale=False
        ),
        carbon_forecast=CarbonForecast(
            currency="IDR", points=carbon_points, stale=False
        ),
    )
