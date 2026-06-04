# Local Endpoint Recipes

`mini-llm-eval-kit` talks to an OpenAI-compatible chat completions endpoint. The examples below are generic starting points. Exact model names, ports, flags, and feature support vary by local server version.

Do not put real API keys or private prompts in public command history, suites, or reports.

## Ollama

Some Ollama setups expose OpenAI-compatible routes at port `11434`:

```bash
mini-llm-eval run \
  --endpoint http://localhost:11434/v1/chat/completions \
  --model llama3.2 \
  --suite examples/basic_suite.toml \
  --out reports/ollama
```

## LM Studio

LM Studio can expose a local OpenAI-compatible server, often on port `1234`:

```bash
mini-llm-eval run \
  --endpoint http://localhost:1234/v1/chat/completions \
  --model local-model \
  --suite examples/regression_suite.toml \
  --out reports/lmstudio
```

## vLLM

For a vLLM OpenAI-compatible server:

```bash
mini-llm-eval run \
  --endpoint http://localhost:8000/v1/chat/completions \
  --model local-model \
  --suite examples/basic_suite.toml \
  --out reports/vllm
```

## llama.cpp Server

For a llama.cpp server with OpenAI-compatible chat completions:

```bash
mini-llm-eval run \
  --endpoint http://localhost:8080/v1/chat/completions \
  --model local-model \
  --suite examples/regression_suite.toml \
  --out reports/llamacpp
```

## Comparing Two Runs

After two runs have written `results.json`, compare them:

```bash
mini-llm-eval compare \
  --baseline reports/before/results.json \
  --candidate reports/after/results.json \
  --out reports/comparison.md
```

Use `--fail-on-regression` in local CI-style checks when a severity increase should return a nonzero exit code.
