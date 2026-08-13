"""Advisor pipeline unit tests — AsyncOpenAI is mocked; no network."""

import asyncio

import pytest

from server.advisor.pipeline import run_pipeline
from server.emissions.calculator import calculate_emissions
from server.emissions.compliance import assess

NOMINAL = {
    "wet_ore_input_tons": 10_000.0,
    "moisture_content_pct": 0.32,
    "nickel_grade_pct": 0.018,
    "reductant_biocoke_pct": 0.0,
    "sec_eaf_kwh_per_t_alloy": 2400.0,
    "power_mix_captive_coal": 1.0,
    "ef_captive_pltu": 1.0,
    "dryer_thermal_efficiency": 0.55,
}

FORECAST = {
    "lmeUsdPerTon": [15400.0],
    "idxCarbonIdrPerTon": [42000.0],
    "taxRateIdrPerTon": 30000.0,
    "marketDepthMedianTco2e": 50000.0,
    "synthetic": True,
    "provenance": {"lmeUsdPerTon": {"synthetic": True}},
}


class _Captured:
    init: dict
    create_kwargs: dict


def _fake_openai(captured: _Captured, content: str = "Total emisi 100.0 tCO2e."):
    class _Msg:
        def __init__(self):
            self.content = content

    class _Choice:
        def __init__(self):
            self.message = _Msg()
            self.finish_reason = "stop"

    class _Resp:
        def __init__(self):
            self.choices = [_Choice()]

    class _Completions:
        async def create(self, **kwargs):
            captured.create_kwargs = kwargs
            return _Resp()

    class _Chat:
        def __init__(self):
            self.completions = _Completions()

    class _Client:
        def __init__(self, **kwargs):
            captured.init = kwargs
            self.chat = _Chat()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

    return _Client


def _collect(result, position, forecast):
    async def _run():
        out = []
        async for event in run_pipeline(result, position, forecast):
            out.append(event)
        return out

    return asyncio.run(_run())


@pytest.fixture
def result_and_position():
    r = calculate_emissions(**NOMINAL)
    pos = assess(r, cap_tco2e=r.total_emissions + 1000)
    return r, pos


def test_pipeline_emits_four_stages(monkeypatch, result_and_position):
    from server.advisor import pipeline

    captured = _Captured()
    r, pos = result_and_position
    body = f"Total emisi {r.total_emissions:.1f} sesuai kuota."
    monkeypatch.setenv("ELICE_API_KEY", "test-key")
    monkeypatch.setenv("ELICE_BASE_URL", "https://gateway.example/uuid/v1")
    monkeypatch.setattr(pipeline, "AsyncOpenAI", _fake_openai(captured, content=body))

    events = _collect(r, pos, FORECAST)

    stages = [(e["stage"], e["status"]) for e in events]
    assert ("retrieve", "running") in stages
    assert ("retrieve", "done") in stages
    assert ("assemble", "done") in stages
    assert ("synthesise", "done") in stages
    assert ("verify", "done") in stages
    verify = next(e for e in events if e["stage"] == "verify" and e["status"] == "done")
    assert verify["payload"]["flagged"] is False
    assert captured.init["base_url"] == "https://gateway.example/uuid/v1"
    assert events[0]["placeholderCitations"] is False


def test_missing_elice_env_fails_synthesise(monkeypatch, result_and_position):
    from server.advisor import pipeline

    monkeypatch.delenv("ELICE_API_KEY", raising=False)
    monkeypatch.delenv("ELICE_BASE_URL", raising=False)
    monkeypatch.setattr(pipeline, "AsyncOpenAI", _fake_openai(_Captured()))

    r, pos = result_and_position
    events = _collect(r, pos, FORECAST)

    assert any(e["stage"] == "synthesise" and e["status"] == "failed" for e in events)
    assert not any(e["stage"] == "verify" for e in events)


def test_corpus_has_verified_clauses():
    from server.advisor.corpus import CORPUS, has_placeholder_text

    assert len(CORPUS) >= 5
    assert has_placeholder_text() is False


def test_deficit_route_prefers_tax_when_credit_above_tax():
    from server.advisor.routes import build_route_comparison

    routes = build_route_comparison(
        deficit_tco2e=1000.0,
        carbon_price_idr=42000.0,
        tax_rate_idr=30000.0,
        market_depth_median_tco2e=50000.0,
    )
    assert routes is not None
    assert routes.chosen_route == "pay_tax"
    assert routes.rejected_route == "buy"
    assert routes.buy_cost_idr == 42_000_000.0
    assert routes.tax_cost_idr == 30_000_000.0
    assert routes.exceeds_observed_depth is False


def test_deficit_route_prefers_buy_when_credit_below_tax():
    from server.advisor.routes import build_route_comparison

    routes = build_route_comparison(
        deficit_tco2e=1000.0,
        carbon_price_idr=25000.0,
        tax_rate_idr=30000.0,
        market_depth_median_tco2e=50000.0,
    )
    assert routes is not None
    assert routes.chosen_route == "buy"
    assert routes.rejected_route == "pay_tax"


def test_invented_numeral_flags_verify(monkeypatch, result_and_position):
    from server.advisor import pipeline

    r, pos = result_and_position
    # Force deficit so route figures are assembled.
    from server.emissions.compliance import assess

    pos = assess(r, cap_tco2e=max(0.0, r.total_emissions - 5000), carbon_price_idr_per_ton=42000.0)
    monkeypatch.setenv("ELICE_API_KEY", "test-key")
    monkeypatch.setenv("ELICE_BASE_URL", "https://gateway.example/uuid/v1")
    monkeypatch.setattr(
        pipeline,
        "AsyncOpenAI",
        _fake_openai(_Captured(), content="Bayar denda 999999999 ton."),
    )

    events = _collect(r, pos, FORECAST)
    verify = next(e for e in events if e["stage"] == "verify" and e["status"] == "done")
    assert verify["payload"]["flagged"] is True
    assert "999999999" in verify["payload"]["unsupported"]
    assemble = next(e for e in events if e["stage"] == "assemble" and e["status"] == "done")
    assert assemble["payload"]["routeComparison"]["chosen_route"] == "pay_tax"
    assert isinstance(verify["payload"]["citations"], list)
