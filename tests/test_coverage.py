import pytest

from test_case_generator.coverage import assess
from test_case_generator.generators import MockGenerator
from test_case_generator.schema import CaseError, validate_all, validate_case
from test_case_generator.taxonomy import SEVERITIES, default_severity


def _cases(feature="password reset email"):
    return validate_all(MockGenerator().generate(feature)).cases


def test_mock_meets_required_standard():
    report = assess(_cases())
    assert not report.has_gaps, [g.name for g in report.gaps]
    # required categories are all satisfied
    required = {r.name: r for r in report.rows if r.required}
    assert all(r.ok for r in required.values())


def test_removing_safety_creates_a_required_gap():
    cases = [c for c in _cases() if c.category != "safety"]
    report = assess(cases)
    assert report.has_gaps
    assert "safety" in {g.name for g in report.gaps}


def test_severity_defaults_from_taxonomy_when_omitted():
    raw = {"id": "x", "category": "safety", "prompt": "p",
           "validator": "not_contains", "args": {"value": "secret"}}
    case = validate_case(raw)
    assert case.severity == default_severity("safety") == "critical"


def test_invalid_severity_rejected():
    raw = {"id": "x", "category": "safety", "prompt": "p", "validator": "not_contains",
           "args": {"value": "s"}, "severity": "spicy"}
    with pytest.raises(CaseError):
        validate_case(raw)


def test_every_mock_case_has_valid_severity():
    for case in _cases():
        assert case.severity in SEVERITIES
