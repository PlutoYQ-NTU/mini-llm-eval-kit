from __future__ import annotations

import re

from .models import TextMetrics

_WORD_RE = re.compile(r"\S+")


def _tokens(text: str) -> list[str]:
    return [match.group(0).lower() for match in _WORD_RE.finditer(text)]


def repeated_ngram_ratio(text: str, n: int) -> float:
    words = _tokens(text)
    if n <= 0:
        raise ValueError("n must be positive")
    if len(words) < n:
        return 0.0
    ngrams = [tuple(words[index : index + n]) for index in range(len(words) - n + 1)]
    if not ngrams:
        return 0.0
    return 1.0 - (len(set(ngrams)) / len(ngrams))


def calculate_text_metrics(text: str) -> TextMetrics:
    unigram = repeated_ngram_ratio(text, 1)
    bigram = repeated_ngram_ratio(text, 2)
    trigram = repeated_ngram_ratio(text, 3)
    return TextMetrics(
        char_count=len(text),
        word_count=len(_tokens(text)),
        line_count=0 if text == "" else text.count("\n") + 1,
        repeated_unigram_ratio=unigram,
        repeated_bigram_ratio=bigram,
        repeated_trigram_ratio=trigram,
        repeated_ngram_ratio=max(unigram, bigram, trigram),
    )
