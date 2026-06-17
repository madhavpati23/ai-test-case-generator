# ai-test-case-generator

Turn a **feature or requirement** into a set of **runnable test cases** — across
risk categories, including edge cases and safety probes — emitted as YAML that
drops straight into [`prompt-regression-suite`](https://github.com/madhavpati23/prompt-regression-suite).

This is a *prompt-driven test-design accelerator*: instead of hand-writing every
case, you describe the feature and get a structured first draft of the suite
(scenario generation + edge-case coverage), then refine. Every generated case is
**validated against a schema before it's written** — a flaky model can never slip
a malformed case into your suite.

```text
$ python -m test_case_generator generate --feature "password reset email" --out-dir prompts
Generator   : mock
Generated   : 8 raw case(s)
Valid       : 8
Wrote 8 case(s) across 6 file(s):
   prompts/consistency.yaml
   prompts/data_validation.yaml
   prompts/edge_cases.yaml
   prompts/hallucination.yaml
   prompts/robustness.yaml
   prompts/safety.yaml
```

## How it fits the toolchain

```
   feature description
          │
          ▼
  ai-test-case-generator   ──►  prompts/*.yaml  ──►  prompt-regression-suite
  (generate + validate cases)    (the contract)      (run + regression-gate outputs)
```

One repo *designs* the tests; the other *runs and regression-gates* them. The
YAML schema is the shared contract between them, so generated suites execute with
no editing — see [`examples/generated/`](examples/generated/) for output that
loads directly into the suite.

## Two modes

- **mock (default)** — a deterministic, offline generator that emits
  feature-agnostic *scaffold* cases (a structured-output contract, an empty-input
  edge case, a prompt-injection safety check, a consistency pair, …). No API key;
  CI-friendly; what the unit tests run against.
- **claude** — when `ANTHROPIC_API_KEY` is set, asks Claude (`claude-opus-4-8`,
  adaptive thinking) to design cases *tailored* to the feature. Its JSON output is
  parsed and **validated case-by-case**; invalid cases are dropped and reported.

```bash
pip install -e ".[dev]"            # or: pip install -r requirements.txt
pytest -q

# Offline (mock):
python -m test_case_generator generate --feature "checkout discount codes" --out-dir prompts

# From a spec file:
python -m test_case_generator generate --spec examples/password-reset.txt --out-dir prompts

# Tailored cases from the real model:
export ANTHROPIC_API_KEY=sk-ant-...
python -m test_case_generator generate --feature "support chatbot answering billing questions" --out-dir prompts
```

## The schema (the contract)

Each case is `{id, category, prompt, validator, args}`.

| Field | Allowed values |
|-------|----------------|
| `category` | accuracy, reasoning, edge_cases, hallucination, consistency, robustness, safety, data_validation |
| `validator` | `contains`, `not_contains`, `regex`, `equals_number`, `json_schema` |

Validator args: `contains`/`not_contains` → `{value}`; `regex` → `{pattern}`;
`equals_number` → `{value}`; `json_schema` → `{properties}`. Validation lives in
[`schema.py`](src/test_case_generator/schema.py) and is exercised by the tests.

## An honest note

The generator produces a **first draft**. Generated cases — especially their
*expected* answers — should be reviewed by a human before being trusted as a
regression baseline. Treat it as an accelerator for test design, not a substitute
for judgment.

## License

MIT — see [LICENSE](LICENSE).
