from __future__ import annotations

import re

from .metrics import calculate_text_metrics
from .models import EvalResult, PromptTest, SEVERITY_ORDER


def pattern_matches(pattern: str, text: str) -> bool:
    if pattern.startswith("re:"):
        try:
            return re.search(pattern[3:], text, flags=re.IGNORECASE | re.MULTILINE) is not None
        except re.error:
            return False
    return pattern.lower() in text.lower()


def _raise_severity(current: str, candidate: str) -> str:
    if SEVERITY_ORDER[candidate] > SEVERITY_ORDER[current]:
        return candidate
    return current


def evaluate_response(test: PromptTest, response: str, request_error: str | None = None) -> EvalResult:
    metrics = calculate_text_metrics(response)
    findings: list[str] = []
    severity = "ok"

    if request_error:
        findings.append(f"request failed: {request_error}")
        severity = "error"
    else:
        if test.expected_patterns and not any(pattern_matches(pattern, response) for pattern in test.expected_patterns):
            findings.append("none of the expected patterns matched")
            severity = _raise_severity(severity, "critical" if test.critical else "warning")

        matched_forbidden = [pattern for pattern in test.forbidden_patterns if pattern_matches(pattern, response)]
        if matched_forbidden:
            findings.append("forbidden pattern matched: " + ", ".join(matched_forbidden))
            severity = _raise_severity(severity, "critical")

        if test.min_chars is not None and metrics.char_count < test.min_chars:
            findings.append(f"response shorter than min_chars ({metrics.char_count} < {test.min_chars})")
            severity = _raise_severity(severity, "critical" if test.critical else "warning")

        if test.max_chars is not None and metrics.char_count > test.max_chars:
            findings.append(f"response longer than max_chars ({metrics.char_count} > {test.max_chars})")
            severity = _raise_severity(severity, "warning")

        if (
            test.max_repeated_ngram_ratio is not None
            and metrics.repeated_ngram_ratio > test.max_repeated_ngram_ratio
        ):
            findings.append(
                "repeated ngram ratio exceeds limit "
                f"({metrics.repeated_ngram_ratio:.3f} > {test.max_repeated_ngram_ratio:.3f})"
            )
            severity = _raise_severity(severity, "warning")

    return EvalResult(
        id=test.id,
        category=test.category,
        prompt=test.prompt,
        response=response,
        passed=severity == "ok",
        severity=severity,
        findings=findings,
        metrics=metrics,
    )
