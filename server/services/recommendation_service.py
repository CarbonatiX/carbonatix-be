"""SSE framing for GET /runs/{run_id}/recommendation (real Elice advisor)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from server.advisor.pipeline import run_pipeline
from server.ai_env import ensure_ai_env, require_advisor_config
from server.emissions.calculator import EmissionResult
from server.emissions.compliance import CompliancePosition
from server.models import create_recommendation
from server.schemas import RunDetail


def _result_from_run(emission: dict) -> EmissionResult:
    return EmissionResult(
        nickel_output_tons=float(emission["nickel_output_tons"]),
        alloy_output_tons=float(emission["alloy_output_tons"]),
        dryer_emissions=float(emission["dryer_emissions"]),
        kiln_heat_emissions=float(emission["kiln_heat_emissions"]),
        kiln_reductant_emissions=float(emission["kiln_reductant_emissions"]),
        eaf_emissions=float(emission["eaf_emissions"]),
        total_emissions=float(emission["total_emissions"]),
        dry_ore_tons=float(emission["dry_ore_tons"]),
        dryer_coal_tons=float(emission["dryer_coal_tons"]),
        kiln_coal_tons=float(emission["kiln_coal_tons"]),
        reductant_tons=float(emission["reductant_tons"]),
        eaf_mwh=float(emission["eaf_mwh"]),
    )


def _position_from_run(compliance: dict, projected: float) -> CompliancePosition:
    """Map Indah compliance (positive surplus) to solo CompliancePosition."""
    cap = float(compliance["period_cap_tco2e"])
    # Solo: position_tco2e = projected - cap (positive deficit).
    solo_position = projected - cap
    return CompliancePosition(
        cap_tco2e=cap,
        projected_tco2e=projected,
        position_tco2e=solo_position,
        is_compliant=projected <= cap,
        position_value_idr=float(compliance.get("value_idr") or 0),
    )


def _forecast_for_prompt(forecast_snapshot: dict) -> dict:
    """Shape run forecast snapshot into the dict `build_prompt` expects.

    Missing prices fail loudly — never invent Rp35,200 / demo constants.
    """
    nickel = (forecast_snapshot or {}).get("nickel") or {}
    carbon = (forecast_snapshot or {}).get("carbon") or {}

    if nickel.get("price_usd_per_ton") is None:
        raise RuntimeError("Forecast unavailable: nickel price missing from run snapshot")
    if carbon.get("limit_price_idr") is None:
        raise RuntimeError("Forecast unavailable: carbon price missing from run snapshot")

    nickel_price = float(nickel["price_usd_per_ton"])
    carbon_price = float(carbon["limit_price_idr"])
    tax_rate = float(carbon.get("tax_rate_idr") or 0)
    market_depth = float(carbon.get("market_depth_median_tco2e") or 0)
    if tax_rate <= 0:
        raise RuntimeError("Forecast unavailable: carbon tax rate missing from run snapshot")

    return {
        "dates": ["snapshot"],
        "lmeUsdPerTon": [nickel_price],
        "lmeUsdPerTonLower": [nickel_price],
        "lmeUsdPerTonUpper": [nickel_price],
        "idxCarbonIdrPerTon": [carbon_price],
        "idxCarbonIdrPerTonLower": [carbon_price],
        "idxCarbonIdrPerTonUpper": [carbon_price],
        "taxRateIdrPerTon": tax_rate,
        "marketDepthMedianTco2e": market_depth,
        "stale": False,
        "synthetic": True,
        "provenance": {
            "lmeUsdPerTon": {"synthetic": True, "warning": "MVP forecast stub"},
            "idxCarbonIdrPerTon": {"synthetic": True, "warning": "MVP forecast stub"},
        },
    }


async def stream_recommendation(db, run: RunDetail, company_id: str) -> AsyncIterator[str]:
    """Yield SSE `data:` lines for the four-stage advisor pipeline."""
    ensure_ai_env()
    try:
        require_advisor_config()
    except RuntimeError as exc:
        event = {
            "stage": "synthesise",
            "status": "failed",
            "payload": {"error": str(exc)},
            "placeholderCitations": False,
        }
        yield f"data: {json.dumps(event)}\n\n"
        return

    emission = run.emission_result
    if isinstance(emission, dict):
        result = _result_from_run(emission)
    else:
        result = _result_from_run(emission.model_dump())

    compliance = run.compliance
    compliance_dict = (
        compliance.model_dump() if hasattr(compliance, "model_dump") else dict(compliance)
    )
    position = _position_from_run(compliance_dict, result.total_emissions)

    forecast_raw = run.forecast_snapshot
    if hasattr(forecast_raw, "model_dump"):
        forecast_raw = forecast_raw.model_dump()
    try:
        forecast = _forecast_for_prompt(forecast_raw or {})
    except RuntimeError as exc:
        event = {
            "stage": "assemble",
            "status": "failed",
            "payload": {"error": str(exc)},
            "placeholderCitations": False,
        }
        yield f"data: {json.dumps(event)}\n\n"
        return

    trace: list[dict] = []
    async for event in run_pipeline(result, position, forecast):
        trace.append(event)
        yield f"data: {json.dumps(event)}\n\n"
        if (
            event.get("stage") == "verify"
            and event.get("status") == "done"
            and isinstance(event.get("payload"), dict)
            and not event["payload"].get("flagged")
        ):
            payload = event["payload"]
            try:
                create_recommendation(
                    db,
                    company_id=company_id,
                    run_id=run.id,
                    trace=trace,
                    text=str(payload.get("body") or ""),
                    citations=list(payload.get("citations") or []),
                    confidence=float(payload.get("confidence") or 0),
                    model_id=str(payload.get("model") or ""),
                )
            except Exception:  # noqa: BLE001 - persistence must not break SSE
                pass
