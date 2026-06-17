import pytest

from test_case_generator.config import ConfigError, load_config
from test_case_generator.coverage import assess, effective_standard
from test_case_generator.generators import MockGenerator
from test_case_generator.schema import validate_all


def _write(tmp_path, text):
    p = tmp_path / "suite.yaml"
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_load_valid_config(tmp_path):
    cfg = load_config(_write(tmp_path, """
feature: "password reset"
ai_type: chatbot
out_dir: out
coverage: {safety: 4, accuracy: 3}
"""))
    assert cfg.feature == "password reset"
    assert cfg.ai_type == "chatbot"
    assert cfg.out_dir == "out"
    assert cfg.coverage == {"safety": 4, "accuracy": 3}


def test_missing_feature_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, "ai_type: chatbot\n"))


def test_unknown_ai_type_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, 'feature: x\nai_type: oracle\n'))


def test_unknown_coverage_category_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_config(_write(tmp_path, 'feature: x\ncoverage: {vibes: 2}\n'))


def test_override_makes_category_required():
    std = effective_standard({"accuracy": 3})
    assert std["accuracy"] == (True, 3)          # now required at 3
    assert std["safety"][0] is True              # default required unchanged


def test_override_can_create_a_gap():
    cases = validate_all(MockGenerator().generate("password reset")).cases
    # mock emits 0 accuracy cases; requiring accuracy must surface a gap
    report = assess(cases, {"accuracy": 3})
    assert report.has_gaps
    assert "accuracy" in {g.name for g in report.gaps}
    # without the override, the same suite meets the standard
    assert not assess(cases).has_gaps
