from __future__ import annotations

import csv
import json
from pathlib import Path

from mini_llm_eval_kit.csv_writer import CSV_COLUMNS, write_csv_results
from mini_llm_eval_kit.evaluators import evaluate_response
from mini_llm_eval_kit.json_writer import write_json_report
from mini_llm_eval_kit.markdown_writer import render_markdown_report
from mini_llm_eval_kit.models import PromptSuite, PromptTest, SuiteMetadata


def _suite_and_results() -> tuple[PromptSuite, list]:
    test = PromptTest(id="identity_001", category="identity", prompt="Who are you?", expected_patterns=["model"])
    suite = PromptSuite(SuiteMetadata("demo", "desc"), [test])
    return suite, [evaluate_response(test, "I am a model.")]


def test_markdown_writer_includes_expected_sections() -> None:
    suite, results = _suite_and_results()
    summary = {"total": 1, "passed": 1, "failed": 0, "warnings": 0, "critical": 0, "errors": 0}
    report = render_markdown_report(suite, {"model": "local-model"}, summary, results)
    for section in [
        "# Mini LLM Eval Report",
        "## Summary",
        "## Configuration",
        "## Results by Category",
        "## Failed or Flagged Tests",
        "## Full Results",
        "## Suggested Next Steps",
        "## Privacy Note",
    ]:
        assert section in report


def test_csv_writer_writes_expected_columns(tmp_path: Path) -> None:
    _, results = _suite_and_results()
    path = tmp_path / "results.csv"
    write_csv_results(path, results)
    with path.open(encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        assert reader.fieldnames == CSV_COLUMNS
        rows = list(reader)
    assert rows[0]["id"] == "identity_001"


def test_json_writer_produces_valid_json(tmp_path: Path) -> None:
    suite, results = _suite_and_results()
    path = tmp_path / "results.json"
    summary = {"total": 1, "passed": 1, "failed": 0, "warnings": 0, "critical": 0, "errors": 0}
    write_json_report(path, suite, {"model": "local-model"}, summary, results)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["passed"] == 1
    assert payload["results"][0]["passed"] is True
