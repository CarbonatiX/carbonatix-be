import pytest

from server.schemas import EmissionRequest
from server.services import emission_service


def test_calculate_emissions_unit(sample_emission_request):
    req = EmissionRequest(**sample_emission_request)
    result = emission_service.calculate_emissions(req).emission_result

    # Real RKEF model (not the old stub). Spot-check structure + formula invariants.
    assert result.dry_ore_tons == pytest.approx(700.0)
    assert result.nickel_output_tons == pytest.approx(9.45)  # 700 * 0.015 * 0.90
    assert result.scope_1 == pytest.approx(
        result.dryer_emissions + result.kiln_heat_emissions + result.kiln_reductant_emissions
    )
    assert result.scope_2 == pytest.approx(result.eaf_emissions)
    assert result.total_emissions == pytest.approx(result.scope_1 + result.scope_2)
    assert result.total_emissions > 300  # stub was ~312; real model is higher
    assert result.intensity_per_tonne_ni is not None


def test_emissions_endpoint_requires_auth(client, sample_emission_request):
    response = client.post("/emissions", json=sample_emission_request)

    assert response.status_code == 401


def test_emissions_endpoint_with_auth(client, auth_headers, sample_emission_request):
    response = client.post(
        "/emissions", json=sample_emission_request, headers=auth_headers
    )

    assert response.status_code == 200
    result = response.json()["emission_result"]
    assert result["nickel_output_tons"] == pytest.approx(9.45)
    assert result["total_emissions"] > 300
    assert "scope_1" in result


def test_commit_run_uses_real_calculator(client, auth_headers, sample_emission_request):
    response = client.post(
        "/runs",
        json={"input_snapshot": sample_emission_request},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()["run"]
    assert body["emission_result"]["nickel_output_tons"] == pytest.approx(9.45)
    assert body["compliance"]["status"] in ("surplus", "deficit")
    assert "period_cap_tco2e" in body["compliance"]

    run_id = body["id"]
    get_resp = client.get(f"/runs/{run_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["run"]["id"] == run_id
