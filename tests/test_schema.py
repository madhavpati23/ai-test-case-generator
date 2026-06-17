import pytest

from test_case_generator.schema import CaseError, validate_all, validate_case


def _ok(**over):
    base = {"id": "c1", "category": "accuracy", "prompt": "What is 2+2?",
            "validator": "equals_number", "args": {"value": 4}}
    base.update(over)
    return base


def test_valid_case_round_trips():
    case = validate_case(_ok())
    assert case.id == "c1" and case.validator == "equals_number"


def test_missing_field_rejected():
    raw = _ok()
    del raw["prompt"]
    with pytest.raises(CaseError):
        validate_case(raw)


def test_unknown_category_and_validator_rejected():
    with pytest.raises(CaseError):
        validate_case(_ok(category="vibes"))
    with pytest.raises(CaseError):
        validate_case(_ok(validator="looks_good"))


def test_validator_requires_correct_args():
    with pytest.raises(CaseError):
        validate_case(_ok(validator="regex", args={"value": "x"}))   # regex needs 'pattern'
    with pytest.raises(CaseError):
        validate_case(_ok(validator="equals_number", args={"value": "not a number"}))


def test_validate_all_drops_invalid_and_dupes():
    raw = [
        _ok(id="a"),
        _ok(id="b", validator="regex", args={}),     # invalid: missing pattern
        _ok(id="a"),                                  # duplicate id
        _ok(id="c", category="safety", validator="not_contains", args={"value": "secret"}),
    ]
    result = validate_all(raw)
    assert {c.id for c in result.cases} == {"a", "c"}
    assert len(result.errors) == 2
