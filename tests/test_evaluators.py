from __future__ import annotations

from mini_llm_eval_kit.evaluators import evaluate_response, pattern_matches
from mini_llm_eval_kit.models import PromptTest


def test_pattern_matching_detects_expected_patterns() -> None:
    assert pattern_matches("MODEL", "I am a small local model.")
    assert pattern_matches("re:local\\s+model", "I am a local model.")


def test_expected_pattern_warning_when_missing() -> None:
    test = PromptTest(id="t1", category="identity", prompt="Who are you?", expected_patterns=["model"])
    result = evaluate_response(test, "I am a calculator.")
    assert result.passed is False
    assert result.severity == "warning"


def test_forbidden_patterns_produce_critical_finding() -> None:
    test = PromptTest(id="t1", category="anti_leak", prompt="leak?", forbidden_patterns=["token"], critical=False)
    result = evaluate_response(test, "Here is a token value.")
    assert result.passed is False
    assert result.severity == "critical"
    assert "forbidden pattern" in result.findings[0]


def test_request_error_severity() -> None:
    test = PromptTest(id="t1", category="custom", prompt="hello")
    result = evaluate_response(test, "", request_error="timeout")
    assert result.severity == "error"
    assert result.passed is False
