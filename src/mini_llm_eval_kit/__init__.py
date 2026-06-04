from __future__ import annotations

from .comparison import ComparisonReport, ResultChange, compare_result_files, render_comparison_markdown
from .evaluators import evaluate_response, pattern_matches
from .metrics import calculate_text_metrics, repeated_ngram_ratio
from .models import EvalResult, PromptSuite, PromptTest, SuiteMetadata, TextMetrics
from .suite_loader import SuiteLoadError, load_suite

__all__ = [
    "EvalResult",
    "ComparisonReport",
    "PromptSuite",
    "PromptTest",
    "ResultChange",
    "SuiteLoadError",
    "SuiteMetadata",
    "TextMetrics",
    "calculate_text_metrics",
    "compare_result_files",
    "evaluate_response",
    "load_suite",
    "pattern_matches",
    "repeated_ngram_ratio",
    "render_comparison_markdown",
]

__version__ = "0.1.0"
