"""Process constants for the RKEF emission model.

Every default below is an UNVALIDATED PLACEHOLDER pending calibration.
They are literature-plausible, not sourced. Do not present figures derived
from them as findings.
"""

import math
from dataclasses import dataclass, fields

__all__ = ["DEFAULT_CONSTANTS", "ProcessConstants"]

_FRACTION_FIELDS = frozenset(
    {"recovery_yield", "alloy_nickel_grade", "kiln_thermal_efficiency"}
)


@dataclass(frozen=True)
class ProcessConstants:
    """Physical and empirical constants of an RKEF line."""

    recovery_yield: float = 0.90
    delta_h_vap: float = 2.60
    lhv_coal: float = 20.0
    ef_coal_thermal: float = 2.20
    kiln_thermal_efficiency: float = 0.55
    k_heat: float = 1.80
    k_stoic: float = 2.00
    ef_reductant: float = 3.20
    alloy_nickel_grade: float = 0.10

    def __post_init__(self) -> None:
        for f in fields(self):
            value = getattr(self, f.name)
            if f.name in _FRACTION_FIELDS:
                if not 0.0 < value <= 1.0:
                    raise ValueError(f"{f.name} must be a fraction in (0, 1], got {value!r}")
            elif not (math.isfinite(value) and value > 0):
                raise ValueError(f"{f.name} must be positive and finite, got {value!r}")


DEFAULT_CONSTANTS = ProcessConstants()
