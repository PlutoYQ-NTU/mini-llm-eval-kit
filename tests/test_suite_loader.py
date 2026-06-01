from __future__ import annotations

from pathlib import Path

import pytest

from mini_llm_eval_kit.suite_loader import SuiteLoadError, load_suite


def test_suite_loader_parses_toml(tmp_path: Path) -> None:
    suite_path = tmp_path / "suite.toml"
    suite_path.write_text(
        '''[suite]
name = "test suite"
description = "demo"

[[tests]]
id = "identity_001"
category = "identity"
prompt = "Who are you?"
expected_patterns = ["model"]
critical = true
''',
        encoding="utf-8",
    )
    suite = load_suite(suite_path)
    assert suite.suite.name == "test suite"
    assert suite.tests[0].id == "identity_001"
    assert suite.tests[0].expected_patterns == ["model"]
    assert suite.tests[0].critical is True


def test_suite_loader_rejects_missing_required_fields(tmp_path: Path) -> None:
    suite_path = tmp_path / "bad.toml"
    suite_path.write_text(
        '''[suite]
name = "bad"

[[tests]]
id = "missing_prompt"
category = "identity"
''',
        encoding="utf-8",
    )
    with pytest.raises(SuiteLoadError, match="prompt"):
        load_suite(suite_path)
