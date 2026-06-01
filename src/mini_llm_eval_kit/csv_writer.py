from __future__ import annotations

import csv
from pathlib import Path

from .models import EvalResult

CSV_COLUMNS = [
    "id",
    "category",
    "passed",
    "severity",
    "char_count",
    "word_count",
    "repeated_ngram_ratio",
    "findings",
    "response",
]


def write_csv_results(path: str | Path, results: list[EvalResult]) -> None:
    with Path(path).open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "id": result.id,
                    "category": result.category,
                    "passed": result.passed,
                    "severity": result.severity,
                    "char_count": result.metrics.char_count,
                    "word_count": result.metrics.word_count,
                    "repeated_ngram_ratio": f"{result.metrics.repeated_ngram_ratio:.6f}",
                    "findings": "; ".join(result.findings),
                    "response": result.response,
                }
            )
