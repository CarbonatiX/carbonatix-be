"""Pure verification helpers — no network."""

from server.ingestion.verify import parse_id_number, verified_value


class _Doc:
    def __init__(self, text: str, score: float = 0.9):
        self._text = text
        self.elements = [type("E", (), {"text": text, "score": score})()]

    def full_text(self):
        return self._text


class _Reading:
    def __init__(self, **kwargs):
        self.basis = kwargs.get("basis")
        self.evidence = kwargs.get("evidence", "")
        self.raw_value = kwargs.get("raw_value")
        self.operands = kwargs.get("operands", [])
        self.operation = kwargs.get("operation", "")


def test_parse_indonesian_thousands():
    assert parse_id_number("10.000") == 10000.0
    assert parse_id_number("1,8") == 1.8


def test_transcribed_value_must_be_in_evidence():
    doc = _Doc("Bijih basah 10.000 ton")
    ok = _Reading(
        basis="transcribed",
        evidence="Bijih basah 10.000 ton",
        raw_value="10.000",
    )
    value, conf = verified_value(ok, doc)
    assert value == 10000.0
    assert conf > 0

    bad = _Reading(
        basis="transcribed",
        evidence="Bijih basah 10.000 ton",
        raw_value="99.999",
    )
    value, conf = verified_value(bad, doc)
    assert value is None
    assert conf == 0.0
