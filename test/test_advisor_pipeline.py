"""Advisor pipeline unit tests — AsyncOpenAI is mocked; no network."""

import asyncio

import pytest

from advisor.pipeline import run_pipeline
from emissions.calculator import calculate_emissions
from emissions.compliance import assess


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
    "idxCarbonIdrPerTon": [35200.0],
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
    from advisor import pipeline

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
    from advisor import pipeline

    monkeypatch.delenv("ELICE_API_KEY", raising=False)
    monkeypatch.delenv("ELICE_BASE_URL", raising=False)
    monkeypatch.setattr(pipeline, "AsyncOpenAI", _fake_openai(_Captured()))

    r, pos = result_and_position
    events = _collect(r, pos, FORECAST)

    assert any(e["stage"] == "synthesise" and e["status"] == "failed" for e in events)
    assert not any(e["stage"] == "verify" for e in events)


def test_corpus_has_verified_clauses():
    from advisor.corpus import CORPUS, has_placeholder_text

    assert len(CORPUS) >= 5
    assert has_placeholder_text() is False
