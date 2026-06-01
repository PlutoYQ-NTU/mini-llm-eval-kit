from __future__ import annotations

from pathlib import Path

from mini_llm_eval_kit.builtins import TEMPLATES
from mini_llm_eval_kit.suite_loader import load_suite


def test_builtin_bilingual_template_contains_expected_utf8_patterns() -> None:
    assert "妯″瀷" in TEMPLATES["bilingual"]
    assert "璇勪及" in TEMPLATES["bilingual"]


def test_basic_suite_example_loads_successfully() -> None:
    suite = load_suite(Path("examples/basic_suite.toml"))
    assert any(test.id == "bilingual_001" for test in suite.tests)


def test_builtin_templates_have_no_question_mark_placeholders() -> None:
    for template in TEMPLATES.values():
        assert "??" not in template


def test_leak_template_avoids_generic_forbidden_words() -> None:
    leak_template = TEMPLATES["leak"]
    assert '"token"' not in leak_template
    assert '"secret"' not in leak_template
    assert '"password"' not in leak_template
    assert "re:sk-" in leak_template