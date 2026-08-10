from schemas import EmissionRequest, EmissionResponse, EmissionResult


def calculate_emissions(req: EmissionRequest) -> EmissionResponse:
    dry_ore_tons = req.wet_ore_input_tons * (1 - req.moisture_content_pct)
    alloy_output_tons = (
        dry_ore_tons * req.nickel_grade_pct / 0.12 if req.nickel_grade_pct else 0
    )
    nickel_output_tons = alloy_output_tons * 0.12

    dryer_coal_tons = dry_ore_tons * 0.01
    kiln_coal_tons = dry_ore_tons * 0.015
    reductant_tons = dry_ore_tons * req.reductant_biocoke_pct * 0.01
    eaf_mwh = alloy_output_tons * req.sec_eaf_kwh_per_t_alloy / 1000

    dryer_emissions = dryer_coal_tons * 2.42
    kiln_heat_emissions = kiln_coal_tons * 2.42
    kiln_reductant_emissions = reductant_tons * 2.42
    eaf_emissions = eaf_mwh * 0.98 * req.ef_captive_pltu

    scope_1 = dryer_emissions + kiln_heat_emissions + kiln_reductant_emissions
    scope_2 = eaf_emissions
    total_emissions = scope_1 + scope_2

    intensity = total_emissions / nickel_output_tons if nickel_output_tons > 0 else None

    return EmissionResponse(
        emission_result=EmissionResult(
            nickel_output_tons=round(nickel_output_tons, 2),
            alloy_output_tons=round(alloy_output_tons, 2),
            dryer_emissions=round(dryer_emissions, 2),
            kiln_heat_emissions=round(kiln_heat_emissions, 2),
            kiln_reductant_emissions=round(kiln_reductant_emissions, 2),
            eaf_emissions=round(eaf_emissions, 2),
            scope_1=round(scope_1, 2),
            scope_2=round(scope_2, 2),
            total_emissions=round(total_emissions, 2),
            intensity_per_tonne_ni=(
                round(intensity, 4) if intensity is not None else None
            ),
            dry_ore_tons=round(dry_ore_tons, 2),
            dryer_coal_tons=round(dryer_coal_tons, 2),
            kiln_coal_tons=round(kiln_coal_tons, 2),
            reductant_tons=round(reductant_tons, 2),
            eaf_mwh=round(eaf_mwh, 2),
        )
    )
