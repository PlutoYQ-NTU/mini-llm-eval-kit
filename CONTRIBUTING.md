# Contributing

Thanks for helping improve `mini-llm-eval-kit`.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Evaluation changes

- Use synthetic prompts and outputs in tests and examples.
- Never commit private prompts, model outputs, training samples, credentials, or patient data.
- Add regression tests for evaluator, metric, client, or report-format changes.
- State expected false-positive and false-negative tradeoffs for heuristic checks.

Security-sensitive findings should follow [SECURITY.md](SECURITY.md) instead of being posted publicly.
