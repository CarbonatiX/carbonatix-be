from server.services import forecast_service


def test_get_forecasts_shape(mock_db):
    result = forecast_service.get_forecasts(mock_db, horizon_days=14)

    assert result.horizon_days == 14
    assert result.generated_at
    assert result.nickel.series_id == "lme_nickel"
    assert result.nickel.available is True
    assert result.nickel.currency_unit == "usd_per_ton"
    assert result.nickel.interval_level == 0.8
    assert len(result.nickel.points) == 14
    assert result.nickel.points[0].value == 15400.0
    assert result.nickel.summary.mean_value == 15400.0
    assert result.nickel.history.lookback_days == 90
    assert result.nickel.model.name == "nickel_stub"
    assert result.nickel.staleness.is_stale is False
    assert isinstance(result.nickel.disclosures, list)

    assert result.carbon.series_id == "idx_carbon"
    assert result.carbon.currency_unit == "idr_per_ton"
    assert len(result.carbon.points) == 14
    assert result.carbon.disclosures


def test_get_forecasts_endpoint(client, auth_headers):
    response = client.get("/forecasts?horizon_days=7", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert "generated_at" in body
    assert body["horizon_days"] == 7
    assert "nickel" in body
    assert "carbon" in body
    assert body["nickel"]["available"] is True
    assert body["nickel"]["currency_unit"] == "usd_per_ton"
    assert len(body["nickel"]["points"]) == 7
    assert "summary" in body["nickel"]
    assert "history" in body["nickel"]
    assert "model" in body["nickel"]
    assert "staleness" in body["nickel"]
    assert "disclosures" in body["nickel"]
