from __future__ import annotations

from mini_llm_eval_kit.metrics import calculate_text_metrics, repeated_ngram_ratio


def test_repeated_ngram_ratio_works() -> None:
    ratio = repeated_ngram_ratio("hello hello hello world", 1)
    assert ratio == 0.5


def test_empty_text_metrics_do_not_crash() -> None:
    metrics = calculate_text_metrics("")
    assert metrics.char_count == 0
    assert metrics.word_count == 0
    assert metrics.line_count == 0
    assert metrics.repeated_ngram_ratio == 0.0
