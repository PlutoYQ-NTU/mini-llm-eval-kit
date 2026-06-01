# Security Policy

`mini-llm-eval-kit` sends prompts only to the endpoint that the user explicitly provides. It does not upload prompts, suites, reports, or model outputs by default, and it has no dependency on the official OpenAI Python SDK.

Reports may contain model outputs with sensitive information. Review generated Markdown, CSV, and JSON files before publishing, sharing, or committing them to a public repository.

Anti-leak checks are heuristic. They can highlight suspicious strings, template contamination, path-like output, or secret-like output, but they cannot prove that a model is safe or free from memorized training data.

Do not include secrets, private training samples, private prompts, credentials, checkpoints, hospital data, research data, or user data in public prompt suites or reports.

If you pass an API key with `--api-key` or `--api-key-env`, the key is sent as an `Authorization: Bearer ...` header only to the endpoint you specified.
