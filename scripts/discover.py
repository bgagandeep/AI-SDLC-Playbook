#!/usr/bin/env python3
"""Phase 0 discovery: record a read-only baseline of the target project."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Marker files that positively identify a stack.
STACK_MARKERS: dict[str, tuple[str, ...]] = {
    "python": ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"),
    "node": ("package.json", "pnpm-workspace.yaml", "yarn.lock", "bun.lockb"),
    "flutter": ("pubspec.yaml",),
    "go": ("go.mod",),
    "rust": ("Cargo.toml",),
    "java_maven": ("pom.xml",),
    "java_gradle": ("build.gradle", "build.gradle.kts"),
    "docker": ("Dockerfile", "docker-compose.yml", "compose.yaml"),
    "terraform": ("main.tf",),
    "github_actions": (".github/workflows",),
}
GLOB_MARKERS: dict[str, tuple[str, ...]] = {"dotnet": ("*.sln", "*.csproj")}


def detect(root: Path) -> dict[str, bool]:
    facts = {"git": (root / ".git").exists()}
    for stack, markers in STACK_MARKERS.items():
        facts[stack] = any((root / marker).exists() for marker in markers)
    for stack, patterns in GLOB_MARKERS.items():
        facts[stack] = any(any(root.glob(pattern)) for pattern in patterns)
    return facts


def git_head(root: Path) -> str | None:
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def unknowns_for(facts: dict[str, bool], commit_sha: str | None) -> list[str]:
    """Discovery cannot observe these statically; they must be filled in by a human or agent."""
    items = [
        "architecture-style",
        "runtime-topology",
        "data-flows-and-classification",
        "external-service-dependencies",
        "deployment-targets",
        "security-boundaries-and-authz-model",
        "observability-coverage",
        "pre-existing-test-lint-security-failures",
        "known-technical-debt",
        "rollback-strategy",
    ]
    if not facts["git"] or commit_sha is None:
        items.append("version-control-history")
    if not any(facts[stack] for stack in STACK_MARKERS if stack != "github_actions"):
        items.append("primary-language-and-stack")
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root to scan.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Report path (default: <root>/discovery/project.json).",
    )
    parser.add_argument("--stdout", action="store_true", help="Print the report instead of writing it.")
    args = parser.parse_args(argv)

    root_label = args.root.as_posix()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory.", file=sys.stderr)
        return 1

    facts = detect(root)
    commit_sha = git_head(root)
    report: dict[str, Any] = {
        "status": "baseline-discovery",
        "root": root_label,
        "commit_sha": commit_sha,
        "facts": {name: {"value": value, "confidence": "verified"} for name, value in facts.items()},
        "unknowns": unknowns_for(facts, commit_sha),
    }
    payload = json.dumps(report, indent=2) + "\n"

    if args.stdout:
        print(payload, end="")
        return 0

    output = args.output or (root / "discovery" / "project.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload)
    print(f"Discovery report written to {output}")
    print(f"  verified facts: {sum(facts.values())}/{len(facts)}   unknowns: {len(report['unknowns'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
