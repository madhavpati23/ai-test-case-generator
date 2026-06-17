"""The test-case schema, shared with prompt-regression-suite, plus validation.

A generated case is only useful if a downstream runner can actually execute it.
This module is the contract: it defines the allowed categories and validators,
and validates every case (especially ones an LLM produced) before we trust it.
Treating model output as untrusted and validating its shape is the "API/data
validation" discipline applied to the generator itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CATEGORIES = {
    "accuracy", "reasoning", "edge_cases", "hallucination",
    "consistency", "robustness", "safety", "data_validation",
}

# validator -> required arg keys (matches prompt-regression-suite's validators)
VALIDATOR_ARGS = {
    "contains": ["value"],
    "not_contains": ["value"],
    "regex": ["pattern"],
    "equals_number": ["value"],
    "json_schema": ["properties"],
}


@dataclass(frozen=True)
class Case:
    id: str
    category: str
    prompt: str
    validator: str
    args: dict[str, Any]


class CaseError(ValueError):
    """Raised when a case does not satisfy the schema."""


def validate_case(raw: dict[str, Any]) -> Case:
    """Validate one raw dict and return a Case, or raise CaseError."""
    for key in ("id", "category", "prompt", "validator", "args"):
        if key not in raw:
            raise CaseError(f"missing field {key!r}")

    cid = raw["id"]
    if not isinstance(cid, str) or not cid.strip():
        raise CaseError("id must be a non-empty string")

    category = raw["category"]
    if category not in CATEGORIES:
        raise CaseError(f"unknown category {category!r}")

    prompt = raw["prompt"]
    if not isinstance(prompt, str) or not prompt.strip():
        raise CaseError(f"{cid}: prompt must be a non-empty string")

    validator = raw["validator"]
    if validator not in VALIDATOR_ARGS:
        raise CaseError(f"{cid}: unknown validator {validator!r}")

    args = raw["args"]
    if not isinstance(args, dict):
        raise CaseError(f"{cid}: args must be an object")
    for required in VALIDATOR_ARGS[validator]:
        if required not in args:
            raise CaseError(f"{cid}: validator {validator!r} requires args.{required}")

    if validator == "equals_number":
        try:
            float(args["value"])
        except (TypeError, ValueError):
            raise CaseError(f"{cid}: equals_number value must be numeric")
    if validator == "json_schema" and not isinstance(args["properties"], dict):
        raise CaseError(f"{cid}: json_schema properties must be an object")

    return Case(id=cid, category=category, prompt=prompt, validator=validator, args=args)


@dataclass
class ValidationResult:
    cases: list[Case]
    errors: list[str]


def validate_all(raw_cases: list[dict[str, Any]]) -> ValidationResult:
    """Validate a batch, dropping (and recording) invalid cases and dup ids."""
    good: list[Case] = []
    errors: list[str] = []
    seen: set[str] = set()
    for i, raw in enumerate(raw_cases):
        try:
            case = validate_case(raw)
        except CaseError as exc:
            errors.append(str(exc))
            continue
        if case.id in seen:
            errors.append(f"duplicate id {case.id!r} (dropped)")
            continue
        seen.add(case.id)
        good.append(case)
    return ValidationResult(cases=good, errors=errors)
