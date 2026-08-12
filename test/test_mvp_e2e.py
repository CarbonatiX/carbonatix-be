"""MVP happy-path: register → commit run with coherent prices (no live Elice)."""

from pricing import CARBON_TAX_RATE_IDR, STUB_CARBON_PRICE_IDR, STUB_NICKEL_PRICE_USD
from services.bundled_twin import REQUIRED_PROCESS_TYPES, ensure_bundled_twin


def test_register_seeds_bundled_twin(client, mock_db):
    response = client.post(
        "/auth/register",
        json={"email": "mvp@example.com", "password": "Passw0rd!"},
    )
    assert response.status_code == 201
    from server.models.user import find_user_by_email

    user = find_user_by_email(mock_db, "mvp@example.com")
    twin = mock_db.twin_models.find_one({"company_id": user["company_id"]})
    assert twin is not None
    types = {n["process_type"] for n in twin["nodes"]}
    assert types == set(REQUIRED_PROCESS_TYPES)


def test_e2e_commit_run_coherent_prices(client, auth_headers, sample_emission_request):
    response = client.post(
        "/runs",
        headers=auth_headers,
        json={"input_snapshot": sample_emission_request},
    )
    assert response.status_code == 201
    run = response.json()["run"]
    carbon = run["forecast_snapshot"]["carbon"]
    nickel = run["forecast_snapshot"]["nickel"]
    assert carbon["limit_price_idr"] == STUB_CARBON_PRICE_IDR
    assert carbon["tax_rate_idr"] == CARBON_TAX_RATE_IDR
    assert nickel["price_usd_per_ton"] == STUB_NICKEL_PRICE_USD
    # Compliance value uses the same carbon stub (IDR magnitude check).
    assert run["compliance"]["value_idr"] >= 0


def test_ensure_bundled_twin_idempotent(mock_db):
    ensure_bundled_twin(mock_db, "co_1")
    ensure_bundled_twin(mock_db, "co_1")
    twins = list(mock_db.twin_models.find({"company_id": "co_1"}))
    assert len(twins) == 1
    assert len(twins[0]["nodes"]) == len(REQUIRED_PROCESS_TYPES)
