import os

import yaml

from test_case_generator.generators import MockGenerator, slugify
from test_case_generator.schema import validate_all
from test_case_generator.serialize import write_suite


def test_slugify():
    assert slugify("Password Reset Email") == "password-reset-email"
    assert slugify("!!!") == "feature"


def test_mock_output_is_all_valid():
    raw = MockGenerator().generate("password reset email")
    result = validate_all(raw)
    assert result.errors == []
    assert len(result.cases) == len(raw) >= 8
    # covers multiple categories, including a safety case
    cats = {c.category for c in result.cases}
    assert "safety" in cats and "data_validation" in cats
    assert len(cats) >= 4


def test_write_suite_groups_by_category(tmp_path):
    raw = MockGenerator().generate("checkout flow")
    cases = validate_all(raw).cases
    paths = write_suite(cases, str(tmp_path))
    assert paths, "expected at least one file"
    # every written file parses and matches the suite format
    for path in paths:
        assert os.path.basename(path).endswith(".yaml")
        doc = yaml.safe_load(open(path, encoding="utf-8"))
        assert "category" in doc and isinstance(doc["cases"], list)
        for c in doc["cases"]:
            assert {"id", "prompt", "validator", "args"} <= c.keys()
