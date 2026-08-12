from server.services import forecast_service


def test_get_forecasts_shape(mock_db):
    result = forecast_service.get_forecasts(mock_db, horizon_days=14)

    assert result.horizon_days == 14
    assert result.generated_at

    nickel = result.nickel
    assert nickel.series_id == "nickel_cash_settlement_usd"
    assert nickel.available is True
    assert nickel.currency_unit == "usd_per_ton"
    assert nickel.interval_level == 0.8
    assert len(nickel.points) == 14
    assert nickel.points[0].price_usd_per_ton == 15400.0
    assert nickel.points[0].provenance.bucket == "short"
    assert nickel.points[13].provenance.bucket == "short"
    assert nickel.summary.mean_usd_per_ton == 15400.0
    assert nickel.history.last_observed_price_usd_per_ton == 15400.0
    assert nickel.model.bucket_models[0].model_class == "stub"
    assert nickel.staleness.is_stale is False
    assert isinstance(nickel.disclosures, list)

    carbon = result.carbon
    assert carbon.series_id == "idx_carbon_regular"
    assert carbon.available is True
    assert carbon.currency_unit == "idr_per_ton"
    assert len(carbon.points) == 14
    assert carbon.points[0].price_idr_per_ton == 42000.0
    assert carbon.summary.mean_idr_per_ton == 42000.0
    assert len(carbon.monthly_anchors) == 1
    assert carbon.market_depth is not None
    assert carbon.model.model_class == "stub"
    assert carbon.disclosures


def test_get_forecasts_bucket_boundaries(mock_db):
    """RFC-006-Nickel-Forecasting-FINAL-v2.md §5.3: short <=13, medium 14-21, long 22-30."""
    result = forecast_service.get_forecasts(mock_db, horizon_days=30)
    buckets = [p.provenance.bucket for p in result.nickel.points]

    assert buckets[13] == "short"
    assert buckets[14] == "medium"
    assert buckets[21] == "medium"
    assert buckets[22] == "long"
    assert buckets[29] == "long"


def test_get_forecasts_endpoint(client, auth_headers):
    response = client.get("/forecasts?horizon_days=7", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert "generated_at" in body
    assert body["horizon_days"] == 7
    assert body["nickel"]["available"] is True
    assert body["nickel"]["currency_unit"] == "usd_per_ton"
    assert len(body["nickel"]["points"]) == 7
    assert "price_usd_per_ton" in body["nickel"]["points"][0]
    assert "provenance" in body["nickel"]["points"][0]
    for key in ("summary", "history", "model", "staleness", "disclosures"):
        assert key in body["nickel"]

    assert body["carbon"]["currency_unit"] == "idr_per_ton"
    assert "price_idr_per_ton" in body["carbon"]["points"][0]
    for key in (
        "summary",
        "monthly_anchors",
        "market_depth",
        "model",
        "staleness",
        "disclosures",
    ):
        assert key in body["carbon"]
