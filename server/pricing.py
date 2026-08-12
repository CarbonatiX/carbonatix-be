"""Single source of MVP stub market figures.

Compliance valuation, forecast stubs, run snapshots, and the advisor must
all quote the same carbon/nickel prices. Disclosed as stub/synthetic on the
UI — not live exchange data.
"""

# Last-observed-style stub (aligned with forecast_service / IDX demo anchor).
STUB_CARBON_PRICE_IDR = 42_000.0
STUB_CARBON_LOWER_IDR = 39_000.0
STUB_CARBON_UPPER_IDR = 46_000.0

STUB_NICKEL_PRICE_USD = 15_400.0
STUB_NICKEL_LOWER_USD = 14_900.0
STUB_NICKEL_UPPER_USD = 15_900.0

# Domestic carbon tax rate used for deficit route comparison (PRD §11).
CARBON_TAX_RATE_IDR = 30_000.0

# Non-zero stub depth so buy recommendations can be checked against liquidity.
STUB_MEDIAN_MONTHLY_VOLUME_TCO2E = 50_000.0
STUB_MAX_MONTHLY_VOLUME_TCO2E = 80_000.0
STUB_TRAILING_12M_VOLUME_TCO2E = 400_000.0

# Advisor escalate threshold (RFC-007: behaviour locked; calibration deferred).
ADVISOR_CONFIDENCE_THRESHOLD = 0.6
