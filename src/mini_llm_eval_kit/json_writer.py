from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import EvalResult, PromptSuite, suite_to_dict


def build_json_payload(
    suite: PromptSuite,
    config: dict[str, Any],
    summary: dict[str, int],
    results: list[EvalResult],
) -> dict[str, Any]:
    return {
        "suite": suite_to_dict(suite),
        "config": config,
        "summary": summary,
        "results": [result.to_dict() for result in results],
    }


def write_json_report(
    path: str | Path,
    suite: PromptSuite,
    config: dict[str, Any],
    summary: dict[str, int],
    results: list[EvalResult],
) -> None:
    payload = build_json_payload(suite, config, summary, results)
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
