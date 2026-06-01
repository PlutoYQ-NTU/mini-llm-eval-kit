from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from .builtins import BUILTIN_CATEGORIES, EVALUATOR_TYPES, TEMPLATES, get_template
from .client import ChatCompletionClient, ClientError
from .csv_writer import write_csv_results
from .evaluators import evaluate_response
from .json_writer import write_json_report
from .markdown_writer import write_markdown_report
from .models import EvalResult, PromptSuite
from .suite_loader import SuiteLoadError, load_suite


def build_summary(results: list[EvalResult]) -> dict[str, int]:
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.passed),
        "failed": sum(1 for result in results if not result.passed),
        "warnings": sum(1 for result in results if result.severity == "warning"),
        "critical": sum(1 for result in results if result.severity == "critical"),
        "errors": sum(1 for result in results if result.severity == "error"),
    }


def _resolve_api_key(api_key: str | None, api_key_env: str | None) -> str | None:
    if api_key:
        return api_key
    if api_key_env:
        return os.environ.get(api_key_env)
    return None


def run_suite(
    suite: PromptSuite,
    client: ChatCompletionClient,
    verbose: bool = False,
) -> list[EvalResult]:
    results: list[EvalResult] = []
    for test in suite.tests:
        if verbose:
            print(f"running {test.id} ({test.category})")
        try:
            response = client.complete(test.prompt)
            result = evaluate_response(test, response)
        except ClientError as exc:
            result = evaluate_response(test, "", request_error=str(exc))
        results.append(result)
    return results


def _write_reports(out_dir: Path, suite: PromptSuite, config: dict[str, object], results: list[EvalResult]) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(results)
    write_markdown_report(out_dir / "eval_report.md", suite, config, summary, results)
    write_csv_results(out_dir / "results.csv", results)
    write_json_report(out_dir / "results.json", suite, config, summary, results)
    return summary


def cmd_run(args: argparse.Namespace) -> int:
    try:
        suite = load_suite(args.suite)
    except SuiteLoadError as exc:
        print(f"suite error: {exc}", file=sys.stderr)
        return 2

    config: dict[str, object] = {
        "endpoint": args.endpoint or "",
        "model": args.model,
        "suite": str(args.suite),
        "out": str(args.out),
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "timeout": args.timeout,
        "api_key_env": args.api_key_env or "",
        "dry_run": args.dry_run,
    }

    if args.dry_run:
        print(f"Dry run: suite '{suite.suite.name}' contains {len(suite.tests)} prompt(s).")
        for test in suite.tests:
            print(f"- {test.id} [{test.category}]: {test.prompt}")
        return 0

    if not args.endpoint:
        print("error: --endpoint is required unless --dry-run is used", file=sys.stderr)
        return 2

    api_key = _resolve_api_key(args.api_key, args.api_key_env)
    client = ChatCompletionClient(
        endpoint=args.endpoint,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        api_key=api_key,
    )
    results = run_suite(suite, client, verbose=args.verbose)
    summary = _write_reports(Path(args.out), suite, config, results)
    print(f"Wrote reports to {args.out}")
    print(
        "Summary: "
        f"{summary['passed']}/{summary['total']} passed, "
        f"warnings={summary['warnings']}, critical={summary['critical']}, errors={summary['errors']}"
    )
    if args.fail_on_critical and (summary["critical"] > 0 or summary["errors"] > 0):
        return 1
    return 0


def cmd_init_suite(args: argparse.Namespace) -> int:
    output_path = Path(args.out)
    if output_path.exists() and not args.force:
        print(f"error: {output_path} already exists; use --force to overwrite", file=sys.stderr)
        return 2
    try:
        template = get_template(args.template)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template, encoding="utf-8")
    print(f"Wrote {args.template} suite to {output_path}")
    return 0


def cmd_list_builtins(args: argparse.Namespace) -> int:
    del args
    print("Categories:")
    for category in BUILTIN_CATEGORIES:
        print(f"- {category}")
    print("\nEvaluator types:")
    for evaluator_type in EVALUATOR_TYPES:
        print(f"- {evaluator_type}")
    print("\nSuite templates:")
    for template in sorted(TEMPLATES):
        print(f"- {template}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mini-llm-eval",
        description="Lightweight evaluation toolkit for small local language models.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a prompt suite against an OpenAI-compatible endpoint.")
    run_parser.add_argument("--endpoint", help="OpenAI-compatible chat completions endpoint.")
    run_parser.add_argument("--model", default="local-model", help="Optional model name. Default: local-model.")
    run_parser.add_argument("--suite", required=True, help="TOML prompt suite path.")
    run_parser.add_argument("--out", default="reports", help="Output directory. Default: reports.")
    run_parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature. Default: 0.0.")
    run_parser.add_argument("--max-tokens", type=int, default=256, help="Maximum tokens. Default: 256.")
    run_parser.add_argument("--timeout", type=float, default=60.0, help="Request timeout in seconds. Default: 60.")
    run_parser.add_argument("--api-key", help="Optional API key.")
    run_parser.add_argument("--api-key-env", help="Optional environment variable name for API key.")
    run_parser.add_argument("--dry-run", action="store_true", help="Validate suite and show planned prompts without calling endpoint.")
    run_parser.add_argument("--fail-on-critical", action="store_true", help="Return nonzero if critical checks fail.")
    run_parser.add_argument("--verbose", action="store_true", help="Print prompt-level progress.")
    run_parser.set_defaults(func=cmd_run)

    init_parser = subparsers.add_parser("init-suite", help="Write a starter TOML prompt suite.")
    init_parser.add_argument("--out", default="eval_suite.toml", help="Output TOML suite path. Default: eval_suite.toml.")
    init_parser.add_argument("--template", default="basic", choices=sorted(TEMPLATES), help="Template name. Default: basic.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite if output file exists.")
    init_parser.set_defaults(func=cmd_init_suite)

    list_parser = subparsers.add_parser("list-builtins", help="Print built-in categories and evaluator types.")
    list_parser.set_defaults(func=cmd_list_builtins)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
