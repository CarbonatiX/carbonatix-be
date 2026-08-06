from server.schemas import EmissionRequest
from server.services import emission_service


def test_calculate_emissions_unit(sample_emission_request):
    req = EmissionRequest(**sample_emission_request)
    result = emission_service.calculate_emissions(req).emission_result

    assert result.dry_ore_tons == 700.0
    assert result.alloy_output_tons == 87.5
    assert result.nickel_output_tons == 10.5
    assert result.dryer_coal_tons == 7.0
    assert result.kiln_coal_tons == 10.5
    assert result.reductant_tons == 0.35
    assert result.eaf_mwh == 280.0
    assert result.dryer_emissions == 16.94
    assert result.kiln_heat_emissions == 25.41
    assert result.kiln_reductant_emissions == 0.85
    assert result.eaf_emissions == 268.91
    assert result.scope_1 == 43.2
    assert result.scope_2 == 268.91
    assert result.total_emissions == 312.11
    assert result.intensity_per_tonne_ni == 29.7247


def test_emissions_endpoint_requires_auth(client, sample_emission_request):
    response = client.post("/emissions", json=sample_emission_request)

    assert response.status_code == 401


def test_emissions_endpoint_with_auth(client, auth_headers, sample_emission_request):
    response = client.post("/emissions", json=sample_emission_request, headers=auth_headers)

    assert response.status_code == 200
    result = response.json()["emission_result"]
    assert result["total_emissions"] == 312.11
    assert result["nickel_output_tons"] == 10.5
