"""Deficit route comparison figures for the advisor (RFC-007 §2.5)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pricing import CARBON_TAX_RATE_IDR


@dataclass(frozen=True)
class RouteComparison:
    deficit_tco2e: float
    carbon_price_idr: float
    tax_rate_idr: float
    buy_cost_idr: float
    tax_cost_idr: float
    abate_tonnes: float
    chosen_route: str  # "buy" | "pay_tax"
    rejected_route: str
    market_depth_median_tco2e: float
    exceeds_observed_depth: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "deficit_tco2e": self.deficit_tco2e,
            "carbon_price_idr": self.carbon_price_idr,
            "tax_rate_idr": self.tax_rate_idr,
            "buy_cost_idr": self.buy_cost_idr,
            "tax_cost_idr": self.tax_cost_idr,
            "abate_tonnes": self.abate_tonnes,
            "chosen_route": self.chosen_route,
            "rejected_route": self.rejected_route,
            "market_depth_median_tco2e": self.market_depth_median_tco2e,
            "exceeds_observed_depth": self.exceeds_observed_depth,
        }

    def figure_entries(self) -> dict[str, str]:
        """Human-labelled figures injected into the prompt + numeral permit set."""
        chosen_label = (
            "Beli kredit (IDR)" if self.chosen_route == "buy" else "Bayar pajak karbon (IDR)"
        )
        rejected_label = (
            "Beli kredit (IDR)" if self.rejected_route == "buy" else "Bayar pajak karbon (IDR)"
        )
        return {
            "Defisit (tCO2e)": f"{self.deficit_tco2e:.1f}",
            "Tarif pajak karbon (IDR/ton)": f"{self.tax_rate_idr:.0f}",
            "Biaya beli kredit (IDR)": f"{self.buy_cost_idr:.0f}",
            "Biaya pajak karbon (IDR)": f"{self.tax_cost_idr:.0f}",
            "Abatemen dibutuhkan (tCO2e)": f"{self.abate_tonnes:.1f}",
            "Kedalaman pasar median bulanan (tCO2e)": f"{self.market_depth_median_tco2e:.0f}",
            f"Rute terpilih — {chosen_label}": (
                f"{self.buy_cost_idr:.0f}"
                if self.chosen_route == "buy"
                else f"{self.tax_cost_idr:.0f}"
            ),
            f"Rute ditolak — {rejected_label}": (
                f"{self.buy_cost_idr:.0f}"
                if self.rejected_route == "buy"
                else f"{self.tax_cost_idr:.0f}"
            ),
        }


def build_route_comparison(
    *,
    deficit_tco2e: float,
    carbon_price_idr: float,
    tax_rate_idr: float = CARBON_TAX_RATE_IDR,
    market_depth_median_tco2e: float,
) -> RouteComparison | None:
    """Compare buy vs tax in IDR; abatement as tonnes only. None when not in deficit."""
    if deficit_tco2e <= 0:
        return None

    buy_cost = deficit_tco2e * carbon_price_idr
    tax_cost = deficit_tco2e * tax_rate_idr
    # Buying is only rational when credit price sits below the tax rate (PRD §11).
    if carbon_price_idr < tax_rate_idr:
        chosen, rejected = "buy", "pay_tax"
    else:
        chosen, rejected = "pay_tax", "buy"

    return RouteComparison(
        deficit_tco2e=deficit_tco2e,
        carbon_price_idr=carbon_price_idr,
        tax_rate_idr=tax_rate_idr,
        buy_cost_idr=buy_cost,
        tax_cost_idr=tax_cost,
        abate_tonnes=deficit_tco2e,
        chosen_route=chosen,
        rejected_route=rejected,
        market_depth_median_tco2e=market_depth_median_tco2e,
        exceeds_observed_depth=deficit_tco2e > market_depth_median_tco2e,
    )
