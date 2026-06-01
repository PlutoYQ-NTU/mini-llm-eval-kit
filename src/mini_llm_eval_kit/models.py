from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SEVERITY_ORDER = {"ok": 0, "warning": 1, "critical": 2, "error": 3}


@dataclass(frozen=True)
class SuiteMetadata:
    name: str
    description: str = ""


@dataclass(frozen=True)
class PromptTest:
    id: str
    category: str
    prompt: str
    expected_patterns: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)
    min_chars: int | None = None
    max_chars: int | None = None
    max_repeated_ngram_ratio: float | None = None
    critical: bool = False
    notes: str = ""


@dataclass(frozen=True)
class PromptSuite:
    suite: SuiteMetadata
    tests: list[PromptTest]


@dataclass(frozen=True)
class TextMetrics:
    char_count: int
    word_count: int
    line_count: int
    repeated_unigram_ratio: float
    repeated_bigram_ratio: float
    repeated_trigram_ratio: float
    repeated_ngram_ratio: float


@dataclass(frozen=True)
class EvalResult:
    id: str
    category: str
    prompt: str
    response: str
    passed: bool
    severity: str
    findings: list[str]
    metrics: TextMetrics

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["metrics"] = asdict(self.metrics)
        return data


def suite_to_dict(prompt_suite: PromptSuite) -> dict[str, Any]:
    return {
        "name": prompt_suite.suite.name,
        "description": prompt_suite.suite.description,
        "tests": [asdict(test) for test in prompt_suite.tests],
    }
