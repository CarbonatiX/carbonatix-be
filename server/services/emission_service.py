from dataclasses import replace

from server.emissions.calculator import calculate_emissions as _calculate
from server.emissions.constants import DEFAULT_CONSTANTS, ProcessConstants
from server.schemas import EmissionRequest, EmissionResponse, EmissionResult


def constants_from_site_spec(site_spec: dict | None) -> ProcessConstants:
    """Overlay company site_spec onto default process constants when present.

    New companies seed site_spec fields as 0.0 placeholders — those are ignored
    so ProcessConstants validation (fractions in (0, 1]) is not tripped.
    """
    if not site_spec:
        return DEFAULT_CONSTANTS
    overrides: dict[str, float] = {}
    for key in ("kiln_thermal_efficiency", "alloy_nickel_grade"):
        raw = site_spec.get(key)
        if raw is None:
            continue
        value = float(raw)
        if 0.0 < value <= 1.0:
            overrides[key] = value
    if not overrides:
        return DEFAULT_CONSTANTS
    return replace(DEFAULT_CONSTANTS, **overrides)


def calculate_emissions(
    req: EmissionRequest,
    *,
    constants: ProcessConstants | None = None,
) -> EmissionResponse:
    raw = _calculate(
        wet_ore_input_tons=req.wet_ore_input_tons,
        moisture_content_pct=req.moisture_content_pct,
        nickel_grade_pct=req.nickel_grade_pct,
        reductant_biocoke_pct=req.reductant_biocoke_pct,
        sec_eaf_kwh_per_t_alloy=req.sec_eaf_kwh_per_t_alloy,
        power_mix_captive_coal=req.power_mix_captive_coal,
        ef_captive_pltu=req.ef_captive_pltu,
        dryer_thermal_efficiency=req.dryer_thermal_efficiency,
        constants=constants or DEFAULT_CONSTANTS,
    )
    intensity = raw.intensity_per_tonne_ni
    return EmissionResponse(
        emission_result=EmissionResult(
            nickel_output_tons=round(raw.nickel_output_tons, 4),
            alloy_output_tons=round(raw.alloy_output_tons, 4),
            dryer_emissions=round(raw.dryer_emissions, 4),
            kiln_heat_emissions=round(raw.kiln_heat_emissions, 4),
            kiln_reductant_emissions=round(raw.kiln_reductant_emissions, 4),
            eaf_emissions=round(raw.eaf_emissions, 4),
            scope_1=round(raw.scope_1, 4),
            scope_2=round(raw.scope_2, 4),
            total_emissions=round(raw.total_emissions, 4),
            intensity_per_tonne_ni=(round(intensity, 4) if intensity is not None else None),
            dry_ore_tons=round(raw.dry_ore_tons, 4),
            dryer_coal_tons=round(raw.dryer_coal_tons, 4),
            kiln_coal_tons=round(raw.kiln_coal_tons, 4),
            reductant_tons=round(raw.reductant_tons, 4),
            eaf_mwh=round(raw.eaf_mwh, 4),
        )
    )
