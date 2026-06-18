from test_case_generator.coverage import assess
from test_case_generator.generators import MockGenerator
from test_case_generator.schema import validate_all
from test_case_generator.taxonomy import TAXONOMY


def test_red_team_is_required_in_the_standard():
    assert "red_team" in TAXONOMY
    assert TAXONOMY["red_team"].required


def test_mock_emits_red_team_and_meets_standard():
    cases = validate_all(MockGenerator().generate("password reset")).cases
    red = [c for c in cases if c.category == "red_team"]
    assert len(red) >= 2
    assert any(c.severity == "critical" for c in red)
    assert not assess(cases).has_gaps   # red_team requirement satisfied
