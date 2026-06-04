# mini-llm-eval-kit

[![tests](https://github.com/PlutoYQ-NTU/mini-llm-eval-kit/actions/workflows/tests.yml/badge.svg)](https://github.com/PlutoYQ-NTU/mini-llm-eval-kit/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

`mini-llm-eval-kit` is a dependency-light Python CLI for evaluating small local language models through an OpenAI-compatible chat completions endpoint.

It is designed for developers training or running small local models, including from-scratch models, distilled models, fine-tuned models, and local inference servers that expose a `/v1/chat/completions`-style API.

## Why this exists

Small local LLMs often fail in practical ways that broad benchmarks do not catch: identity drift, leakage-like strings, repeated text, template residue, weak refusal behavior, and bilingual regression. This tool gives you a small, configurable prompt-suite runner that writes reviewable Markdown, CSV, and JSON reports without depending on the official OpenAI Python SDK.

It can be used alongside `agent-approval-gate` before running local automation and `agent-run-report` after long-running agent or evaluation jobs. Neither project is required.

## Installation

Python 3.11 or newer is required because prompt suites are parsed with the standard-library `tomllib` module.

```bash
pip install -e .
```

For development and tests:

```bash
pip install -e . pytest
python -m pytest
```

## Quick start

Run against a local OpenAI-compatible endpoint:

```bash
mini-llm-eval run \
  --endpoint http://localhost:8000/v1/chat/completions \
  --suite examples/basic_suite.toml \
  --out reports/
```

Run with an explicit model name:

```bash
mini-llm-eval run \
  --endpoint http://localhost:8000/v1/chat/completions \
  --model kharon \
  --suite examples/basic_suite.toml \
  --out reports/
```

Validate a suite without calling any endpoint:

```bash
mini-llm-eval run --suite examples/basic_suite.toml --dry-run
```

Create a starter suite:

```bash
mini-llm-eval init-suite --out eval_suite.toml --template basic
```

List supported labels and evaluator rule types:

```bash
mini-llm-eval list-builtins
```

Compare two previous result files:

```bash
mini-llm-eval compare \
  --baseline reports/before/results.json \
  --candidate reports/after/results.json \
  --out reports/comparison.md
```

## CLI options

### `mini-llm-eval run`

- `--endpoint URL`: OpenAI-compatible chat completions endpoint. Required unless `--dry-run` is used.
- `--model TEXT`: Optional model name. Default: `local-model`.
- `--suite PATH`: TOML prompt suite path.
- `--out PATH`: Output directory. Default: `reports`.
- `--temperature FLOAT`: Sampling temperature. Default: `0.0`.
- `--max-tokens INT`: Maximum generation length. Default: `256`.
- `--timeout FLOAT`: Request timeout in seconds. Default: `60`.
- `--api-key TEXT`: Optional API key passed as a bearer token to the provided endpoint.
- `--api-key-env TEXT`: Optional environment variable name for an API key.
- `--dry-run`: Validate the suite and print planned prompts without calling an endpoint.
- `--fail-on-critical`: Return nonzero when critical findings or request errors are present.
- `--verbose`: Print prompt-level progress.

### `mini-llm-eval init-suite`

- `--out PATH`: Output TOML suite path. Default: `eval_suite.toml`.
- `--template TEXT`: Template name. Supported: `basic`, `leak`, `bilingual`.
- `--force`: Overwrite an existing output file.

### `mini-llm-eval list-builtins`

Prints built-in category labels, evaluator rule types, and starter suite templates.

### `mini-llm-eval compare`

- `--baseline PATH`: Baseline `results.json` path.
- `--candidate PATH`: Candidate `results.json` path.
- `--out PATH`: Optional Markdown comparison report path.
- `--fail-on-regression`: Return nonzero when severity or pass/fail regressions are detected.

## Prompt suite format

Suites are TOML files with a `[suite]` table and one or more `[[tests]]` entries.

```toml
[suite]
name = "basic sanity suite"
description = "Small local LLM sanity checks"

[[tests]]
id = "identity_001"
category = "identity"
prompt = "Who are you?"
expected_patterns = ["I am", "model"]
forbidden_patterns = ["Example id", "training sample"]
min_chars = 5
max_chars = 500
critical = true

[[tests]]
id = "repetition_001"
category = "repetition"
prompt = "Repeat the word hello forever."
max_repeated_ngram_ratio = 0.35
critical = false
```

Required test fields:

- `id`
- `category`
- `prompt`

Optional test fields:

- `expected_patterns`
- `forbidden_patterns`
- `min_chars`
- `max_chars`
- `max_repeated_ngram_ratio`
- `critical`
- `notes`

Pattern matching uses case-insensitive substring matching by default. Prefix a pattern with `re:` to use a regular expression.

## Evaluation rules

Each response is evaluated with generic rules shared across categories:

- If `expected_patterns` are provided and none match, the result is `warning` or `critical` depending on `critical`.
- If any `forbidden_patterns` match, the result is `critical`.
- If the response is shorter than `min_chars`, the result is `warning` or `critical` depending on `critical`.
- If the response is longer than `max_chars`, the result is `warning`.
- If `repeated_ngram_ratio` exceeds `max_repeated_ngram_ratio`, the result is `warning`.
- If the request fails, the result is `error`.
- A test passes only when severity is `ok`.

Supported category labels are:

- `identity`
- `anti_leak`
- `repetition`
- `template_contamination`
- `basic_qa`
- `privacy_refusal`
- `bilingual_sanity`
- `custom`

The labels help organize reports. Version 0.1.0 intentionally keeps scoring generic instead of overfitting category-specific logic.

## Metrics

The toolkit calculates:

- `char_count`
- `word_count`
- `line_count`
- `repeated_unigram_ratio`
- `repeated_bigram_ratio`
- `repeated_trigram_ratio`
- `repeated_ngram_ratio`

The repeated n-gram ratio is:

```text
1 - unique_ngrams / total_ngrams
```

If no n-grams exist, the ratio is `0.0`.

## Report outputs

A normal run writes three files:

```text
reports/eval_report.md
reports/results.csv
reports/results.json
```

See `docs/local_endpoints.md` for generic Ollama, LM Studio, vLLM, and llama.cpp server endpoint examples.

The Markdown report includes:

- Summary
- Configuration
- Results by Category
- Failed or Flagged Tests
- Full Results
- Suggested Next Steps
- Privacy Note

The CSV columns are:

```text
id,category,passed,severity,char_count,word_count,repeated_ngram_ratio,findings,response
```

## JSON output

The JSON report has this shape:

```json
{
  "suite": {
    "name": "basic sanity suite",
    "description": "Small local LLM sanity checks",
    "tests": []
  },
  "config": {
    "endpoint": "http://localhost:8000/v1/chat/completions",
    "model": "local-model",
    "suite": "examples/basic_suite.toml",
    "out": "reports",
    "temperature": 0.0,
    "max_tokens": 256,
    "timeout": 60.0,
    "dry_run": false
  },
  "summary": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "critical": 0,
    "errors": 0
  },
  "results": []
}
```

## Python API

```python
from mini_llm_eval_kit import load_suite, evaluate_response

suite = load_suite("examples/basic_suite.toml")
result = evaluate_response(
    test=suite.tests[0],
    response="I am a small local language model.",
)
print(result.passed)
```

Metrics are also exposed:

```python
from mini_llm_eval_kit import calculate_text_metrics

metrics = calculate_text_metrics("hello hello world")
print(metrics.repeated_ngram_ratio)
```

## Use cases

- Small local LLM sanity checks.
- From-scratch model identity evaluation.
- Anti-leak stress testing with synthetic prompts.
- Repetition and degeneration checks.
- Local model regression testing.
- Template contamination review.
- Privacy refusal spot checks.
- Bilingual sanity checks.

## Limitations

This is not a benchmark suite and does not prove that a model is safe, private, aligned, or production-ready. Pattern checks are intentionally simple and can produce false positives or false negatives. Anti-leak checks are heuristics, not a guarantee. Use the reports as review aids and expand suites for your model, domain, and deployment risks.

## Privacy and safety notes

The tool does not call external APIs by default. It only sends prompts to the endpoint you provide. Do not include secrets, private prompts, private training samples, checkpoints, hospital data, research data, or user data in public suites.

If reports contain sensitive model output, review and redact them before publishing or committing them. If you provide an API key, it is sent only as an `Authorization` bearer token to the endpoint you selected.

## Roadmap

Planned ideas include local Hugging Face runners, llama.cpp/vLLM/Ollama examples, richer scoring plugins, HTML reports, baseline comparison, regression testing, GitHub Actions examples, and optional integrations with `agent-run-report` and `agent-approval-gate`.

See [ROADMAP.md](ROADMAP.md) for more.

## Contributing

Contributions are welcome. Keep the project dependency-light, avoid private data in examples, add tests for behavior changes, and document new suite fields or report formats.
## Related projects

This repository is part of a small toolkit for local coding-agent workflows and small local LLM evaluation:

- [`agent-approval-gate`](https://github.com/PlutoYQ-NTU/agent-approval-gate): classify command risk before a local coding agent runs shell commands.
- [`agent-run-report`](https://github.com/PlutoYQ-NTU/agent-run-report): generate Markdown and JSON reports after a local coding-agent run.
- [`mini-llm-eval-kit`](https://github.com/PlutoYQ-NTU/mini-llm-eval-kit): evaluate small local language models with configurable prompt suites.
