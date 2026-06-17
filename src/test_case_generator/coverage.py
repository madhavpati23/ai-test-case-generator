"""Measure a suite against the coverage standard in taxonomy.py.

Turns "did we test enough?" from a judgement call into a policy: required
categories must meet their minimum case count, or the suite has a gap. This is
what lets a manager gate a release on coverage rather than vibes.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schema import Case
from .taxonomy import TAXONOMY


@dataclass
class CategoryCoverage:
    name: str
    count: int
    min_cases: int
    required: bool

    @property
    def ok(self) -> bool:
        return self.count >= self.min_cases

    @property
    def is_gap(self) -> bool:
        return self.required and not self.ok


@dataclass
class CoverageReport:
    rows: list[CategoryCoverage]
    total_cases: int

    @property
    def gaps(self) -> list[CategoryCoverage]:
        return [r for r in self.rows if r.is_gap]

    @property
    def has_gaps(self) -> bool:
        return bool(self.gaps)


def assess(cases: list[Case]) -> CoverageReport:
    counts: dict[str, int] = {}
    for case in cases:
        counts[case.category] = counts.get(case.category, 0) + 1
    rows = [
        CategoryCoverage(name=spec.name, count=counts.get(spec.name, 0),
                         min_cases=spec.min_cases, required=spec.required)
        for spec in TAXONOMY.values()
    ]
    return CoverageReport(rows=rows, total_cases=len(cases))


def render(report: CoverageReport) -> str:
    line = "-" * 60
    out = [line, "  COVERAGE vs STANDARD", line]
    for r in sorted(report.rows, key=lambda x: (not x.required, x.name)):
        tag = "REQUIRED" if r.required else "optional"
        if r.is_gap:
            mark = "GAP "
        elif r.ok:
            mark = "ok  "
        else:
            mark = "--  "  # optional, below target — informational only
        out.append(f"  [{mark}] {r.name:<16} {r.count}/{r.min_cases:<3} ({tag})")
    out.append(line)
    if report.has_gaps:
        names = ", ".join(r.name for r in report.gaps)
        out.append(f"  RESULT: BELOW STANDARD — required gaps in: {names}")
    else:
        out.append("  RESULT: meets the required coverage standard.")
    out.append(line)
    return "\n".join(out)
