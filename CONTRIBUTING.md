# Contributing

`mini-llm-eval-kit` is intentionally small and dependency-light. Contributions should keep local model evaluation easy to run and easy to inspect.

## Development

```bash
pip install -e ".[dev]"
python -m pytest
```

## Prompt Suites

When adding suite fields or examples:

- Do not include private prompts, private training samples, credentials, or real user data.
- Keep examples generic and reproducible.
- Add loader or evaluator tests for new fields.
- Update README or docs when the suite format changes.

## Evaluation Behavior

Pattern checks are review aids, not safety guarantees. Avoid claims that a model is safe, private, aligned, or production-ready based only on these reports.

## Pull Requests

Before opening a pull request:

- Run `python -m pytest`.
- Add tests for CLI, suite loading, evaluator, metric, or report behavior changes.
- Update `CHANGELOG.md` for user-visible changes.
