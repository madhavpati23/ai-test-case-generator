from test_case_generator.generators import MockGenerator, short_label
from test_case_generator.schema import validate_all

STORY = """As a user, I want to reset my password via email.
Acceptance criteria:
- A reset link is emailed and expires in 30 minutes
- The link works only once
- Unknown emails get a neutral response
"""


def test_short_label_uses_first_line():
    assert short_label(STORY).startswith("As a user, I want to reset")
    assert len(short_label(STORY)) <= 80


def test_long_user_story_generates_valid_concise_cases():
    cases = validate_all(MockGenerator().generate(STORY)).cases
    assert len(cases) >= 8
    # IDs stay concise (slug of the label), not the whole story
    assert all(len(c.id) <= 80 for c in cases)
    # prompts embed the short label, not the entire multi-line story
    assert all("\n" not in c.prompt for c in cases)
