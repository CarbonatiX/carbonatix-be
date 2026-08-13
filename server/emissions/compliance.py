"""Compliance position against an absolute carbon allocation."""

import math
from dataclasses import dataclass

from server.emissions.calculator import EmissionResult

__all__ = ["CompliancePosition", "assess", "suggest_cap_from_baseline"]

from server.pricing import STUB_CARBON_PRICE_IDR

# Same stub used by forecast_service / advisor (disclosed as synthetic on UI).
DEFAULT_CARBON_PRICE_IDR = STUB_CARBON_PRICE_IDR


@dataclass(frozen=True)
class CompliancePosition:
    """position_tco2e is signed: positive deficit, negative surplus (solo convention)."""

    cap_tco2e: float
    projected_tco2e: float
    position_tco2e: float
    is_compliant: bool
    position_value_idr: float


def assess(
    result: EmissionResult,
    *,
    cap_tco2e: float,
    carbon_price_idr_per_ton: float = DEFAULT_CARBON_PRICE_IDR,
) -> CompliancePosition:
    if not (math.isfinite(cap_tco2e) and cap_tco2e >= 0):
        raise ValueError(
            f"cap_tco2e must be non-negative and finite, got {cap_tco2e!r}"
        )
    if not (math.isfinite(carbon_price_idr_per_ton) and carbon_price_idr_per_ton >= 0):
        raise ValueError(
            f"carbon_price_idr_per_ton must be non-negative and finite, "
            f"got {carbon_price_idr_per_ton!r}"
        )

    projected = result.total_emissions
    position = projected - cap_tco2e
    return CompliancePosition(
        cap_tco2e=cap_tco2e,
        projected_tco2e=projected,
        position_tco2e=position,
        is_compliant=projected <= cap_tco2e,
        position_value_idr=abs(position) * carbon_price_idr_per_ton,
    )


def suggest_cap_from_baseline(
    baseline_total_tco2e: float,
    *,
    reduction_target: float,
) -> float:
    if not 0.0 <= reduction_target < 1.0:
        raise ValueError(
            f"reduction_target must be a fraction in [0, 1), got {reduction_target!r}"
        )
    if not (math.isfinite(baseline_total_tco2e) and baseline_total_tco2e >= 0):
        raise ValueError(
            f"baseline_total_tco2e must be non-negative and finite, got {baseline_total_tco2e!r}"
        )
    return baseline_total_tco2e * (1.0 - reduction_target)
