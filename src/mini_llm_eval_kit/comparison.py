from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEVERITY_ORDER = {"ok": 0, "warning": 1, "critical": 2, "error": 3}


@dataclass(frozen=True)
class ResultChange:
    test_id: str
    category: str
    change_type: str
    baseline_severity: str = ""
    candidate_severity: str = ""
    baseline_passed: bool | None = None
    candidate_passed: bool | None = None


@dataclass(frozen=True)
class ComparisonReport:
    baseline_path: str
    candidate_path: str
    baseline_total: int
    candidate_total: int
    unchanged: int
    improved: int
    regressed: int
    added: int
    removed: int
    pass_to_fail: int
    fail_to_pass: int
    changes: list[ResultChange]

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_path": self.baseline_path,
            "candidate_path": self.candidate_path,
            "baseline_total": self.baseline_total,
            "candidate_total": self.candidate_total,
            "unchanged": self.unchanged,
            "improved": self.improved,
            "regressed": self.regressed,
            "added": self.added,
            "removed": self.removed,
            "pass_to_fail": self.pass_to_fail,
            "fail_to_pass": self.fail_to_pass,
            "changes": [change.__dict__ for change in self.changes],
        }


def compare_result_files(baseline_path: str | Path, candidate_path: str | Path) -> ComparisonReport:
    baseline = _load_results(baseline_path)
    candidate = _load_results(candidate_path)
    baseline_by_id = {str(item["id"]): item for item in baseline}
    candidate_by_id = {str(item["id"]): item for item in candidate}

    changes: list[ResultChange] = []
    unchanged = improved = regressed = pass_to_fail = fail_to_pass = 0

    for test_id in sorted(set(baseline_by_id) | set(candidate_by_id)):
        before = baseline_by_id.get(test_id)
        after = candidate_by_id.get(test_id)
        if before is None and after is not None:
            changes.append(_change(test_id, after, "added"))
            continue
        if after is None and before is not None:
            changes.append(_change(test_id, before, "removed"))
            continue
        assert before is not None and after is not None
        before_severity = str(before.get("severity", ""))
        after_severity = str(after.get("severity", ""))
        before_passed = bool(before.get("passed", False))
        after_passed = bool(after.get("passed", False))
        if before_severity == after_severity and before_passed == after_passed:
            unchanged += 1
            continue

        before_rank = SEVERITY_ORDER.get(before_severity, 99)
        after_rank = SEVERITY_ORDER.get(after_severity, 99)
        if after_rank > before_rank or (before_passed and not after_passed):
            change_type = "regressed"
            regressed += 1
        elif after_rank < before_rank or (not before_passed and after_passed):
            change_type = "improved"
            improved += 1
        else:
            change_type = "changed"

        if before_passed and not after_passed:
            pass_to_fail += 1
        if not before_passed and after_passed:
            fail_to_pass += 1
        changes.append(_change(test_id, after, change_type, before))

    added = sum(1 for change in changes if change.change_type == "added")
    removed = sum(1 for change in changes if change.change_type == "removed")
    return ComparisonReport(
        baseline_path=str(baseline_path),
        candidate_path=str(candidate_path),
        baseline_total=len(baseline),
        candidate_total=len(candidate),
        unchanged=unchanged,
        improved=improved,
        regressed=regressed,
        added=added,
        removed=removed,
        pass_to_fail=pass_to_fail,
        fail_to_pass=fail_to_pass,
        changes=changes,
    )


def render_comparison_markdown(report: ComparisonReport) -> str:
    lines = [
        "# Evaluation Comparison",
        "",
        "## Summary",
        "",
        f"- Baseline: `{report.baseline_path}` ({report.baseline_total} result(s))",
        f"- Candidate: `{report.candidate_path}` ({report.candidate_total} result(s))",
        f"- Unchanged: {report.unchanged}",
        f"- Improved: {report.improved}",
        f"- Regressed: {report.regressed}",
        f"- Added: {report.added}",
        f"- Removed: {report.removed}",
        f"- Pass to fail: {report.pass_to_fail}",
        f"- Fail to pass: {report.fail_to_pass}",
        "",
        "## Changes",
        "",
    ]
    if not report.changes:
        lines.append("No behavior changes detected.")
    else:
        for change in report.changes:
            lines.append(
                "- "
                f"{change.test_id} ({change.category}): {change.change_type}; "
                f"{change.baseline_severity or 'missing'} -> {change.candidate_severity or 'missing'}"
            )
    lines.append("")
    return "\n".join(lines)


def _load_results(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    results = payload.get("results")
    if not isinstance(results, list):
        raise ValueError(f"{path} does not contain a results list")
    return [item for item in results if isinstance(item, dict) and "id" in item]


def _change(
    test_id: str,
    current: dict[str, Any],
    change_type: str,
    baseline: dict[str, Any] | None = None,
) -> ResultChange:
    baseline = baseline or {}
    return ResultChange(
        test_id=test_id,
        category=str(current.get("category") or baseline.get("category") or "unknown"),
        change_type=change_type,
        baseline_severity=str(baseline.get("severity", "")),
        candidate_severity=str(current.get("severity", "")),
        baseline_passed=baseline.get("passed") if "passed" in baseline else None,
        candidate_passed=current.get("passed") if "passed" in current else None,
    )
