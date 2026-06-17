# ai-test-case-generator

Turn a **feature or requirement** into a set of **runnable test cases** — across
risk categories, including edge cases and safety probes — emitted as YAML that
drops straight into [`prompt-regression-suite`](https://github.com/madhavpati23/prompt-regression-suite).

This is a *prompt-driven test-design accelerator*: instead of hand-writing every
case, you describe the feature and get a structured first draft of the suite
(scenario generation + edge-case coverage), then refine. Every generated case is
**validated against a schema before it's written** — a flaky model can never slip
a malformed case into your suite.

It's built to be a **team standard, not a one-off script**. A documented method
([TESTING_PLAYBOOK.md](TESTING_PLAYBOOK.md)) defines the risk taxonomy, a severity
rubric, and a ship / no-ship policy; a **coverage standard** ([taxonomy.py](src/test_case_generator/taxonomy.py))
is enforced by the tool and CI so "did we test enough?" is policy, not opinion.

```text
$ python -m test_case_generator generate --feature "password reset email" --out-dir prompts
Generator   : mock
Generated   : 13 raw case(s)
Valid       : 13
Wrote 13 case(s) across 7 file(s) to prompts
------------------------------------------------------------
  COVERAGE vs STANDARD
------------------------------------------------------------
  [ok  ] edge_cases       2/2   (REQUIRED)
  [ok  ] hallucination    2/2   (REQUIRED)
  [ok  ] robustness       2/1   (REQUIRED)
  [ok  ] safety           3/3   (REQUIRED)
  ...
  RESULT: meets the required coverage standard.
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

## Coverage standard (the team bar)

The tool measures every suite against the required risk categories and can fail
CI if a suite is below standard:

```bash
python -m test_case_generator coverage --prompts prompts --strict
```

```text
------------------------------------------------------------
  COVERAGE vs STANDARD
------------------------------------------------------------
  [ok  ] edge_cases       2/2   (REQUIRED)
  [ok  ] hallucination    2/2   (REQUIRED)
  [ok  ] robustness       2/1   (REQUIRED)
  [ok  ] safety           3/3   (REQUIRED)
  [--  ] accuracy         0/2   (optional)
  ...
  RESULT: meets the required coverage standard.
```

`generate --strict` and `coverage --strict` exit `2` when required categories
are unmet — wire either into CI as a gate (a [`Jenkinsfile`](Jenkinsfile) and a
GitHub Actions workflow both do this). The bar lives in
[`taxonomy.py`](src/test_case_generator/taxonomy.py); the rationale is in the
[playbook](TESTING_PLAYBOOK.md).

## Config-driven runs (`suite.yaml`)

For repeatable, reviewable runs, declare the feature in a config file checked in
next to what it tests — so the whole team generates identically:

```yaml
# suite.yaml
feature: "password reset email assistant"
ai_type: chatbot          # chatbot | rag | classifier | summarizer | agent
out_dir: prompts
coverage:                 # per-feature overrides; each becomes REQUIRED at min N
  safety: 4               # stricter than the org default of 3
  accuracy: 3             # make accuracy REQUIRED for this feature
```

```bash
test-case-generator generate --config suite.yaml --strict
test-case-generator coverage --prompts prompts --config suite.yaml --strict
```

A category named under `coverage` becomes **required** at that minimum — that's
how a high-risk feature raises the bar above the org default in
[`taxonomy.py`](src/test_case_generator/taxonomy.py). `ai_type` tells the Claude
generator where to weight cases (per [the playbook](TESTING_PLAYBOOK.md) §8).
See [`examples/suite.example.yaml`](examples/suite.example.yaml).

## The schema (the contract)

Each case is `{id, category, prompt, validator, args, severity}`.

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
