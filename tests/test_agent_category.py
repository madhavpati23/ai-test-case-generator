from test_case_generator.generators import MockGenerator
from test_case_generator.schema import validate_all
from test_case_generator.taxonomy import CATEGORIES


def test_agent_is_a_known_category():
    assert "agent" in CATEGORIES


def test_no_agent_cases_for_non_agent_feature():
    cases = validate_all(MockGenerator().generate("password reset", ai_type="chatbot")).cases
    assert not any(c.category == "agent" for c in cases)


def test_agent_scaffolds_added_for_agent_ai_type():
    cases = validate_all(MockGenerator().generate("support agent", ai_type="agent")).cases
    agent_cases = [c for c in cases if c.category == "agent"]
    assert len(agent_cases) >= 2
    # the unauthorized-action case is critical
    assert any(c.severity == "critical" for c in agent_cases)
