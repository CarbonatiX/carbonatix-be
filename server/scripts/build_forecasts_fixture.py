"""Build data/forecasts_mvp.json from carbonatix-ml artifacts.

Run once with the ML venv (needs prophet):

  cd carbonatix-ml
  .venv\\Scripts\\python.exe ..\\carbonatix-be\\server\\scripts\\build_forecasts_fixture.py

Writes carbonatix-be/data/forecasts_mvp.json shaped as ForecastsResponse.
"""
from __future__ import annotations

import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

BE_ROOT = Path(__file__).resolve().parents[2]
ML_ROOT = BE_ROOT.parent / "carbonatix-ml"
SERVER_DIR = BE_ROOT / "server"
OUT_PATH = BE_ROOT / "data" / "forecasts_mvp.json"

NICKEL_PROTOTYPE = (
    ML_ROOT
    / "artifacts"
    / "nickel"
    / "prototype"
    / "nickel_forecast_output_prototype_20260809T124300Z.json"
)
CARBON_PKL = ML_ROOT / "artifacts" / "carbon_prophet_20260810.pkl"

HORIZON_DAYS = 30
CARBON_MODEL_META_KEYS = (
    "model_id",
    "model_class",
    "prophet_version",
    "trained_at",
    "training_data",
    "generator_seed",
    "generator_series_sha256",
    "artefact_sha256",
    "band_source",
    "band_sigma_monthly_log",
)


def _load_nickel() -> dict:
    raw = json.loads(NICKEL_PROTOTYPE.read_text(encoding="utf-8"))
    envelope = raw["forecasts"]["30"]
    nickel = envelope["nickel"]
    # Prototype uses list windows; BE schema accepts tuple via coercion.
    if nickel.get("history") and isinstance(nickel["history"].get("window"), list):
        nickel["history"]["window"] = tuple(nickel["history"]["window"])
    return nickel


def _load_carbon() -> dict:
    sys.path.insert(0, str(ML_ROOT))
    from carbon.forecasting.contract import to_payload_dict  # noqa: E402

    with CARBON_PKL.open("rb") as f:
        model = pickle.load(f)
    forecast = model.predict(
        horizon_days=HORIZON_DAYS,
        disclosures=[
            "synthetic_daily_by_type_validation_target",
            "monthly_anchors_are_real",
            "thin_market_depth",
        ],
    )
    payload = to_payload_dict(forecast)

    if payload.get("model"):
        payload["model"] = {
            k: payload["model"][k] for k in CARBON_MODEL_META_KEYS if k in payload["model"]
        }

    anchors = []
    for a in payload.get("monthly_anchors") or []:
        vwap = a.get("vwap_idr_per_ton")
        if vwap is None:
            continue
        anchors.append(
            {
                "month": a["month"],
                "vwap_idr_per_ton": float(vwap),
                "volume_tco2e": float(a.get("volume_tco2e") or 0.0),
                "value_idr": float(a.get("value_idr") or 0.0),
                "transaction_count": int(a.get("transaction_count") or 0),
            }
        )
    payload["monthly_anchors"] = anchors

    if payload.get("market_depth") and isinstance(payload["market_depth"].get("window"), list):
        payload["market_depth"]["window"] = tuple(payload["market_depth"]["window"])

    return payload


def main() -> None:
    if not NICKEL_PROTOTYPE.exists():
        raise SystemExit(f"missing nickel prototype: {NICKEL_PROTOTYPE}")
    if not CARBON_PKL.exists():
        raise SystemExit(f"missing carbon artifact: {CARBON_PKL}")

    nickel = _load_nickel()
    carbon = _load_carbon()
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    payload = {
        "generated_at": generated_at,
        "horizon_days": HORIZON_DAYS,
        "nickel": nickel,
        "carbon": carbon,
    }

    sys.path.insert(0, str(SERVER_DIR))
    from schemas import ForecastsResponse  # noqa: E402

    validated = ForecastsResponse(**payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(validated.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )

    summary = validated.carbon.summary
    print(f"wrote {OUT_PATH}")
    print(f"nickel points: {len(validated.nickel.points)}")
    print(f"carbon points: {len(validated.carbon.points)}")
    print(
        "carbon last_observed_vwap_idr_per_ton:",
        summary.last_observed_vwap_idr_per_ton if summary else None,
    )
    print(
        "nickel last_observed:",
        validated.nickel.history.last_observed_price_usd_per_ton
        if validated.nickel.history
        else None,
    )


if __name__ == "__main__":
    main()
