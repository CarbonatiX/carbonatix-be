from datetime import datetime, timedelta, timezone

from models import get_latest_forecast
from schemas import (
    CarbonForecast,
    CarbonMarketDepth,
    CarbonModelMeta,
    CarbonMonthlyAnchor,
    CarbonPoint,
    CarbonSummary,
    ForecastsResponse,
    NickelBucketModel,
    NickelForecast,
    NickelHistory,
    NickelModelMeta,
    NickelPoint,
    NickelPointProvenance,
    NickelSummary,
    Staleness,
)

_NICKEL_STUB_PRICE = 15400.0
_NICKEL_STUB_LOWER = 14900.0
_NICKEL_STUB_UPPER = 15900.0
_CARBON_STUB_PRICE = 42000.0
_CARBON_STUB_LOWER = 39000.0
_CARBON_STUB_UPPER = 46000.0


def _bucket_for_offset(day_offset: int) -> str:
    """RFC-006-Nickel-Forecasting-FINAL-v2.md §5.3 horizon buckets."""
    if day_offset <= 13:
        return "short"
    if day_offset <= 21:
        return "medium"
    return "long"


def _build_nickel(*, dates: list[str], generated_at: str) -> NickelForecast:
    points = [
        NickelPoint(
            date=d,
            price_usd_per_ton=_NICKEL_STUB_PRICE,
            lower_usd_per_ton=_NICKEL_STUB_LOWER,
            upper_usd_per_ton=_NICKEL_STUB_UPPER,
            provenance=NickelPointProvenance(
                bucket=_bucket_for_offset(i),
                model_id="nickel_stub_v0",
                cache_status="miss",
            ),
        )
        for i, d in enumerate(dates)
    ]
    prices = [p.price_usd_per_ton for p in points]
    return NickelForecast(
        series_id="nickel_cash_settlement_usd",
        available=True,
        currency_unit="usd_per_ton",
        interval_level=0.8,
        points=points,
        summary=NickelSummary(
            mean_usd_per_ton=sum(prices) / len(prices),
            horizon_end_usd_per_ton=prices[-1],
            trend="flat",
            trend_confidence=0.0,
            change_pct=0.0,
        ),
        history=NickelHistory(
            window=(dates[0], dates[0]),
            last_observed_price_usd_per_ton=_NICKEL_STUB_PRICE,
            last_observed_date=dates[0],
        ),
        model=NickelModelMeta(
            bucket_models=[
                NickelBucketModel(
                    bucket="short", model_class="stub", trained_at=generated_at
                ),
            ],
            dataset_version="stub",
            feature_set_version="stub",
            ruleset_version="stub_v0",
        ),
        staleness=Staleness(is_stale=False, as_of=generated_at, age_hours=0.0),
        disclosures=[],
    )


def _build_carbon(*, dates: list[str], generated_at: str) -> CarbonForecast:
    points = [
        CarbonPoint(
            date=d,
            price_idr_per_ton=_CARBON_STUB_PRICE,
            lower_idr_per_ton=_CARBON_STUB_LOWER,
            upper_idr_per_ton=_CARBON_STUB_UPPER,
        )
        for d in dates
    ]
    prices = [p.price_idr_per_ton for p in points]
    last_observed_month = dates[0][:7]
    return CarbonForecast(
        series_id="idx_carbon_regular",
        available=True,
        currency_unit="idr_per_ton",
        interval_level=0.8,
        points=points,
        summary=CarbonSummary(
            mean_idr_per_ton=sum(prices) / len(prices),
            horizon_end_idr_per_ton=prices[-1],
            last_observed_month=last_observed_month,
            last_observed_vwap_idr_per_ton=_CARBON_STUB_PRICE,
            trend="flat",
            trend_confidence=0.0,
            change_pct=0.0,
        ),
        monthly_anchors=[
            CarbonMonthlyAnchor(
                month=last_observed_month,
                vwap_idr_per_ton=_CARBON_STUB_PRICE,
                volume_tco2e=0.0,
                value_idr=0.0,
                transaction_count=0,
            ),
        ],
        market_depth=CarbonMarketDepth(
            window=(last_observed_month, last_observed_month),
            median_monthly_volume_tco2e=0.0,
            max_monthly_volume_tco2e=0.0,
            trailing_12m_volume_tco2e=0.0,
        ),
        model=CarbonModelMeta(
            model_id="carbon_stub_v0",
            model_class="stub",
            prophet_version="n/a",
            trained_at=generated_at,
            training_data="stub",
            generator_seed=0,
            generator_series_sha256="",
            artefact_sha256="",
            band_source="stub",
            band_sigma_monthly_log=0.0,
        ),
        staleness=Staleness(is_stale=False, as_of=generated_at, age_hours=0.0),
        disclosures=[
            (
                "Carbon path is a synthetic daily series anchored to "
                "published IDX monthly aggregates."
            )
        ],
    )


def get_forecasts(db, horizon_days: int = 14) -> ForecastsResponse:
    cached = get_latest_forecast(db)
    if cached:
        payload = {k: v for k, v in cached.items() if k not in ("_id", "updated_at")}
        return ForecastsResponse(**payload)

    generated_at = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date()
    dates = [(today + timedelta(days=i)).isoformat() for i in range(horizon_days)]

    return ForecastsResponse(
        generated_at=generated_at,
        horizon_days=horizon_days,
        nickel=_build_nickel(dates=dates, generated_at=generated_at),
        carbon=_build_carbon(dates=dates, generated_at=generated_at),
    )
