from __future__ import annotations

from pathlib import Path
from typing import Any
import tomllib

from .models import PromptSuite, PromptTest, SuiteMetadata

REQUIRED_TEST_FIELDS = {"id", "category", "prompt"}
OPTIONAL_TEST_FIELDS = {
    "expected_patterns",
    "forbidden_patterns",
    "min_chars",
    "max_chars",
    "max_repeated_ngram_ratio",
    "critical",
    "notes",
}
KNOWN_FIELDS = REQUIRED_TEST_FIELDS | OPTIONAL_TEST_FIELDS


class SuiteLoadError(ValueError):
    """Raised when a prompt suite cannot be loaded or validated."""


def _ensure_list_of_strings(value: Any, field_name: str, test_id: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SuiteLoadError(f"test '{test_id}' field '{field_name}' must be a list of strings")
    return value


def _optional_int(value: Any, field_name: str, test_id: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        raise SuiteLoadError(f"test '{test_id}' field '{field_name}' must be an integer")
    return value


def _optional_float(value: Any, field_name: str, test_id: str) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        raise SuiteLoadError(f"test '{test_id}' field '{field_name}' must be a number")
    return float(value)


def _parse_test(raw: dict[str, Any], index: int) -> PromptTest:
    missing = sorted(REQUIRED_TEST_FIELDS - set(raw))
    test_label = raw.get("id", f"#{index + 1}")
    if missing:
        raise SuiteLoadError(f"test {test_label} is missing required field(s): {', '.join(missing)}")

    unknown = sorted(set(raw) - KNOWN_FIELDS)
    if unknown:
        raise SuiteLoadError(f"test {test_label} has unknown field(s): {', '.join(unknown)}")

    for field_name in REQUIRED_TEST_FIELDS:
        if not isinstance(raw[field_name], str) or not raw[field_name].strip():
            raise SuiteLoadError(f"test {test_label} field '{field_name}' must be a non-empty string")

    return PromptTest(
        id=raw["id"],
        category=raw["category"],
        prompt=raw["prompt"],
        expected_patterns=_ensure_list_of_strings(raw.get("expected_patterns"), "expected_patterns", raw["id"]),
        forbidden_patterns=_ensure_list_of_strings(raw.get("forbidden_patterns"), "forbidden_patterns", raw["id"]),
        min_chars=_optional_int(raw.get("min_chars"), "min_chars", raw["id"]),
        max_chars=_optional_int(raw.get("max_chars"), "max_chars", raw["id"]),
        max_repeated_ngram_ratio=_optional_float(
            raw.get("max_repeated_ngram_ratio"), "max_repeated_ngram_ratio", raw["id"]
        ),
        critical=bool(raw.get("critical", False)),
        notes=str(raw.get("notes", "")),
    )


def load_suite(path: str | Path) -> PromptSuite:
    suite_path = Path(path)
    try:
        data = tomllib.loads(suite_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SuiteLoadError(f"suite not found: {suite_path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise SuiteLoadError(f"invalid TOML in {suite_path}: {exc}") from exc

    raw_suite = data.get("suite", {})
    if not isinstance(raw_suite, dict):
        raise SuiteLoadError("[suite] must be a TOML table")
    suite_name = raw_suite.get("name", suite_path.stem)
    suite_description = raw_suite.get("description", "")
    if not isinstance(suite_name, str) or not suite_name.strip():
        raise SuiteLoadError("suite.name must be a non-empty string")
    if not isinstance(suite_description, str):
        raise SuiteLoadError("suite.description must be a string")

    raw_tests = data.get("tests")
    if not isinstance(raw_tests, list) or not raw_tests:
        raise SuiteLoadError("suite must contain at least one [[tests]] entry")
    tests: list[PromptTest] = []
    seen_ids: set[str] = set()
    for index, raw_test in enumerate(raw_tests):
        if not isinstance(raw_test, dict):
            raise SuiteLoadError(f"test #{index + 1} must be a TOML table")
        parsed = _parse_test(raw_test, index)
        if parsed.id in seen_ids:
            raise SuiteLoadError(f"duplicate test id: {parsed.id}")
        seen_ids.add(parsed.id)
        tests.append(parsed)

    return PromptSuite(suite=SuiteMetadata(name=suite_name, description=suite_description), tests=tests)
