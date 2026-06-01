from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .models import EvalResult, PromptSuite


def suggested_next_steps(results: list[EvalResult]) -> list[str]:
    failed_categories = {result.category for result in results if result.severity != "ok"}
    has_errors = any(result.severity == "error" for result in results)
    suggestions: list[str] = []

    if {"anti_leak", "template_contamination"} & failed_categories:
        suggestions.append("Review training data filters and prompt templates for leakage or template contamination risks.")
    if "repetition" in failed_categories:
        suggestions.append("Adjust decoding parameters or add anti-repetition checks for repetition failures.")
    if "identity" in failed_categories:
        suggestions.append("Add targeted identity examples or improve system prompt handling.")
    if "privacy_refusal" in failed_categories:
        suggestions.append("Improve refusal data and privacy guardrails for privacy-related prompts.")
    if has_errors:
        suggestions.append("Check the endpoint URL, model name, timeout, and local server logs for request errors.")
    if not suggestions:
        suggestions.append("All tests passed; manually review outputs and expand the suite for your model's risk areas.")
    return suggestions


def _escape_cell(value: object) -> str:
    text = str(value).replace("|", "\\|").replace("\n", " ")
    return text


def render_markdown_report(
    suite: PromptSuite,
    config: dict[str, Any],
    summary: dict[str, int],
    results: list[EvalResult],
) -> str:
    lines: list[str] = ["# Mini LLM Eval Report", ""]

    lines.extend([
        "## Summary",
        "",
        f"- Suite: {suite.suite.name}",
        f"- Total tests: {summary['total']}",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Warnings: {summary['warnings']}",
        f"- Critical: {summary['critical']}",
        f"- Errors: {summary['errors']}",
        "",
        "## Configuration",
        "",
    ])
    for key, value in sorted(config.items()):
        display = "<provided>" if key == "api_key" and value else value
        lines.append(f"- {key}: {display}")
    lines.append("")

    lines.extend(["## Results by Category", ""])
    by_category: dict[str, list[EvalResult]] = defaultdict(list)
    for result in results:
        by_category[result.category].append(result)
    lines.extend(["| Category | Total | Passed | Flagged |", "| --- | ---: | ---: | ---: |"])
    for category in sorted(by_category):
        category_results = by_category[category]
        passed = sum(1 for result in category_results if result.passed)
        flagged = len(category_results) - passed
        lines.append(f"| {_escape_cell(category)} | {len(category_results)} | {passed} | {flagged} |")
    lines.append("")

    flagged_results = [result for result in results if result.severity != "ok"]
    lines.extend(["## Failed or Flagged Tests", ""])
    if flagged_results:
        lines.extend(["| ID | Category | Severity | Findings |", "| --- | --- | --- | --- |"])
        for result in flagged_results:
            findings = "; ".join(result.findings) or "flagged"
            lines.append(
                f"| {_escape_cell(result.id)} | {_escape_cell(result.category)} | "
                f"{_escape_cell(result.severity)} | {_escape_cell(findings)} |"
            )
    else:
        lines.append("No failed or flagged tests.")
    lines.append("")

    lines.extend(["## Full Results", ""])
    for result in results:
        lines.extend([
            f"### {result.id}",
            "",
            f"- Category: {result.category}",
            f"- Passed: {result.passed}",
            f"- Severity: {result.severity}",
            f"- Findings: {'; '.join(result.findings) if result.findings else 'none'}",
            f"- Metrics: chars={result.metrics.char_count}, words={result.metrics.word_count}, repeated_ngram_ratio={result.metrics.repeated_ngram_ratio:.3f}",
            "",
            "Prompt:",
            "",
            "```text",
            result.prompt,
            "```",
            "",
            "Response:",
            "",
            "```text",
            result.response,
            "```",
            "",
        ])

    lines.extend(["## Suggested Next Steps", ""])
    for suggestion in suggested_next_steps(results):
        lines.append(f"- {suggestion}")
    lines.extend([
        "",
        "## Privacy Note",
        "",
        "Prompts and model outputs may contain sensitive information. Review reports before publishing, sharing, or committing them.",
        "",
    ])
    return "\n".join(lines)


def write_markdown_report(
    path: str | Path,
    suite: PromptSuite,
    config: dict[str, Any],
    summary: dict[str, int],
    results: list[EvalResult],
) -> None:
    Path(path).write_text(render_markdown_report(suite, config, summary, results), encoding="utf-8")
