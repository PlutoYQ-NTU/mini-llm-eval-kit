# Changelog

## v0.1.1 - Unreleased

### Added

- Added GitHub Actions CI.
- Added issue templates.
- Added README badges.
- Added related-project links.

### Fixed

- Fixed broken bilingual suite examples caused by encoding issues.
- Reduced false positives in synthetic anti-leak example patterns.

## v0.1.0 - 2026-06-02

Initial release.

- Added `mini-llm-eval` CLI with `run`, `init-suite`, and `list-builtins` commands.
- Added dependency-free OpenAI-compatible chat completions client using `urllib.request`.
- Added TOML prompt suite loader for Python 3.11+.
- Added generic evaluators for identity, anti-leak, repetition, template contamination, QA, privacy refusal, bilingual sanity, and custom checks.
- Added Markdown, CSV, and JSON report writers.
- Added example prompt suites, sample reports, and pytest coverage.