import pytest

from test_case_generator.coverage import assess
from test_case_generator.generators import MockGenerator
from test_case_generator.schema import CaseError, validate_all, validate_case


def _base(**over):
    base = {"id": "c1", "category": "safety", "prompt": "p",
            "validator": "not_contains", "args": {"value": "x"}}
    base.update(over)
    return base


def test_default_status_is_draft():
    case = validate_case(_base())
    assert case.status == "draft" and case.reviewer is None


def test_approved_requires_reviewer():
    with pytest.raises(CaseError):
        validate_case(_base(status="approved"))            # no reviewer
    ok = validate_case(_base(status="approved", reviewer="madhav"))
    assert ok.status == "approved" and ok.reviewer == "madhav"


def test_invalid_status_rejected():
    with pytest.raises(CaseError):
        validate_case(_base(status="rubber-stamped"))


def test_generated_cases_start_as_draft():
    cases = validate_all(MockGenerator().generate("password reset")).cases
    assert all(c.status == "draft" for c in cases)


def test_approved_only_view_is_empty_for_fresh_draft_suite():
    cases = validate_all(MockGenerator().generate("password reset")).cases
    approved = [c for c in cases if c.status == "approved"]
    assert approved == []                                  # nothing approved yet
    # the full draft suite meets coverage, but the release (approved) view is empty
    assert not assess(cases).has_gaps
    assert assess(approved).has_gaps                       # 0 approved -> every required gap
