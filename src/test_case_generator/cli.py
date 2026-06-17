"""Command-line entrypoint.

  python -m test_case_generator generate --feature "password reset email" --out-dir prompts
  python -m test_case_generator generate --spec feature.txt --out-dir prompts

Generates cases (mock by default, Claude if ANTHROPIC_API_KEY is set), validates
every one against the schema, drops invalid cases (reporting why), and writes the
survivors as prompt-regression-suite YAML.
"""

from __future__ import annotations

import argparse
import sys

from .generators import get_generator
from .schema import validate_all
from .serialize import write_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="test_case_generator")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="generate a test suite for a feature")
    src = gen.add_mutually_exclusive_group(required=True)
    src.add_argument("--feature", help="feature/requirement described inline")
    src.add_argument("--spec", help="path to a file describing the feature")
    gen.add_argument("--out-dir", default="prompts", help="where to write the YAML suite")

    args = parser.parse_args(argv)

    feature = args.feature
    if args.spec:
        with open(args.spec, encoding="utf-8") as fh:
            feature = fh.read().strip()
    if not feature:
        print("error: empty feature description", file=sys.stderr)
        return 1

    generator = get_generator()
    raw = generator.generate(feature)
    result = validate_all(raw)

    print(f"Generator   : {generator.name}")
    print(f"Generated   : {len(raw)} raw case(s)")
    print(f"Valid       : {len(result.cases)}")
    if result.errors:
        print(f"Dropped     : {len(result.errors)}")
        for err in result.errors:
            print(f"   - {err}")

    if not result.cases:
        print("No valid cases to write.", file=sys.stderr)
        return 1

    paths = write_suite(result.cases, args.out_dir)
    print(f"Wrote {len(result.cases)} case(s) across {len(paths)} file(s):")
    for path in paths:
        print(f"   {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
