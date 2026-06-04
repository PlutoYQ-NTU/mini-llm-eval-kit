from __future__ import annotations

import json
from pathlib import Path

from mini_llm_eval_kit.comparison import compare_result_files, render_comparison_markdown


def write_results(path: Path, results: list[dict[str, object]]) -> None:
    path.write_text(json.dumps({"results": results}), encoding="utf-8")


def test_compare_result_files_detects_regression_and_improvement(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_results(
        baseline,
        [
            {"id": "identity", "category": "identity", "passed": True, "severity": "ok"},
            {"id": "privacy", "category": "privacy_refusal", "passed": False, "severity": "critical"},
            {"id": "removed", "category": "custom", "passed": True, "severity": "ok"},
        ],
    )
    write_results(
        candidate,
        [
            {"id": "identity", "category": "identity", "passed": False, "severity": "warning"},
            {"id": "privacy", "category": "privacy_refusal", "passed": True, "severity": "ok"},
            {"id": "added", "category": "custom", "passed": True, "severity": "ok"},
        ],
    )

    report = compare_result_files(baseline, candidate)

    assert report.regressed == 1
    assert report.improved == 1
    assert report.added == 1
    assert report.removed == 1
    assert report.pass_to_fail == 1
    assert report.fail_to_pass == 1


def test_render_comparison_markdown_includes_summary(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_results(baseline, [{"id": "a", "category": "custom", "passed": True, "severity": "ok"}])
    write_results(candidate, [{"id": "a", "category": "custom", "passed": False, "severity": "warning"}])

    markdown = render_comparison_markdown(compare_result_files(baseline, candidate))

    assert "# Evaluation Comparison" in markdown
    assert "Regressed: 1" in markdown
    assert "a (custom): regressed" in markdown
