"""Expected carbon emission for one RKEF production interval.

Scope 1: dryer combustion, kiln heating, kiln reductant.
Scope 2: electric arc furnace (captive coal share only).

Biocoke reductant and hydro grid power are treated as zero-emission.
"""

import math
from dataclasses import dataclass

from server.emissions.constants import DEFAULT_CONSTANTS, ProcessConstants

__all__ = ["EmissionResult", "calculate_emissions"]

_KWH_PER_MWH = 1_000.0


@dataclass(frozen=True)
class EmissionResult:
    nickel_output_tons: float
    alloy_output_tons: float
    dryer_emissions: float
    kiln_heat_emissions: float
    kiln_reductant_emissions: float
    eaf_emissions: float
    total_emissions: float
    dry_ore_tons: float
    dryer_coal_tons: float
    kiln_coal_tons: float
    reductant_tons: float
    eaf_mwh: float

    @property
    def scope_1(self) -> float:
        return self.dryer_emissions + self.kiln_heat_emissions + self.kiln_reductant_emissions

    @property
    def scope_2(self) -> float:
        return self.eaf_emissions

    @property
    def intensity_per_tonne_ni(self) -> float | None:
        if self.nickel_output_tons == 0:
            return None
        return self.total_emissions / self.nickel_output_tons


def calculate_emissions(
    *,
    wet_ore_input_tons: float,
    moisture_content_pct: float,
    nickel_grade_pct: float,
    reductant_biocoke_pct: float,
    sec_eaf_kwh_per_t_alloy: float,
    power_mix_captive_coal: float,
    ef_captive_pltu: float,
    dryer_thermal_efficiency: float,
    constants: ProcessConstants = DEFAULT_CONSTANTS,
) -> EmissionResult:
    _validate(
        wet_ore_input_tons=wet_ore_input_tons,
        moisture_content_pct=moisture_content_pct,
        nickel_grade_pct=nickel_grade_pct,
        reductant_biocoke_pct=reductant_biocoke_pct,
        sec_eaf_kwh_per_t_alloy=sec_eaf_kwh_per_t_alloy,
        power_mix_captive_coal=power_mix_captive_coal,
        ef_captive_pltu=ef_captive_pltu,
        dryer_thermal_efficiency=dryer_thermal_efficiency,
    )

    dry_fraction = 1.0 - moisture_content_pct
    nickel_output_tons = (
        wet_ore_input_tons * dry_fraction * nickel_grade_pct * constants.recovery_yield
    )

    water_tons = wet_ore_input_tons * moisture_content_pct
    dryer_coal_tons = (water_tons * constants.delta_h_vap) / (
        constants.lhv_coal * dryer_thermal_efficiency
    )
    dryer_emissions = dryer_coal_tons * constants.ef_coal_thermal

    dry_ore_tons = wet_ore_input_tons * dry_fraction
    kiln_coal_tons = (dry_ore_tons * constants.k_heat) / (
        constants.lhv_coal * constants.kiln_thermal_efficiency
    )
    kiln_heat_emissions = kiln_coal_tons * constants.ef_coal_thermal

    fossil_reductant_share = 1.0 - reductant_biocoke_pct
    reductant_tons = nickel_output_tons * constants.k_stoic * fossil_reductant_share
    kiln_reductant_emissions = reductant_tons * constants.ef_reductant

    alloy_output_tons = nickel_output_tons / constants.alloy_nickel_grade
    eaf_mwh = (alloy_output_tons * sec_eaf_kwh_per_t_alloy) / _KWH_PER_MWH
    eaf_emissions = eaf_mwh * (power_mix_captive_coal * ef_captive_pltu)

    total_emissions = (
        dryer_emissions + kiln_heat_emissions + kiln_reductant_emissions + eaf_emissions
    )

    return EmissionResult(
        nickel_output_tons=nickel_output_tons,
        alloy_output_tons=alloy_output_tons,
        dryer_emissions=dryer_emissions,
        kiln_heat_emissions=kiln_heat_emissions,
        kiln_reductant_emissions=kiln_reductant_emissions,
        eaf_emissions=eaf_emissions,
        total_emissions=total_emissions,
        dry_ore_tons=dry_ore_tons,
        dryer_coal_tons=dryer_coal_tons,
        kiln_coal_tons=kiln_coal_tons,
        reductant_tons=reductant_tons,
        eaf_mwh=eaf_mwh,
    )


def _validate(
    *,
    wet_ore_input_tons: float,
    moisture_content_pct: float,
    nickel_grade_pct: float,
    reductant_biocoke_pct: float,
    sec_eaf_kwh_per_t_alloy: float,
    power_mix_captive_coal: float,
    ef_captive_pltu: float,
    dryer_thermal_efficiency: float,
) -> None:
    fractions = {
        "moisture_content_pct": moisture_content_pct,
        "nickel_grade_pct": nickel_grade_pct,
        "reductant_biocoke_pct": reductant_biocoke_pct,
        "power_mix_captive_coal": power_mix_captive_coal,
    }
    for name, value in fractions.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{name} must be a fraction between 0 and 1, got {value!r} "
                f"(percentages such as 32 should be passed as 0.32)"
            )

    non_negative = {
        "wet_ore_input_tons": wet_ore_input_tons,
        "sec_eaf_kwh_per_t_alloy": sec_eaf_kwh_per_t_alloy,
        "ef_captive_pltu": ef_captive_pltu,
    }
    for name, value in non_negative.items():
        if not (math.isfinite(value) and value >= 0):
            raise ValueError(f"{name} must be non-negative, got {value!r}")

    if not 0.0 < dryer_thermal_efficiency <= 1.0:
        raise ValueError(
            "dryer_thermal_efficiency must be a fraction in (0, 1], got "
            f"{dryer_thermal_efficiency!r}"
        )
